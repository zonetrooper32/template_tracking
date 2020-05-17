"""
Hyperplane Tracker
The main implementation for Hyperplane tracker.

# References:
https://pdfs.semanticscholar.org/f06d/3fc49dca2e6380969b3d8f377b33c6001e7a.pdf
https://pdfs.semanticscholar.org/7fbc/4c4f01eb9716959ffef8b4a620a3d1c38577.pdf
http://www.roboticsproceedings.org/rss09/p44.pdf
"""

import os
import sys

import numpy as np
import cv2
import matplotlib.pyplot as plt
from sklearn import linear_model
from tracking import utils

class HyperplaneTracker():
    """Main class for hyperplane tracker.
    """
    def __init__(self, 
                 config):
        self.config = config        # Store configuration
        self.initialized = False    # Flags for tracker status

        if config.DEBUG:
            self._trajectories = []  # Option to store all updating warp trajectories
            self._all_corners = []   # Option to store all corners produced during tracking, including iterations

    def initialize(self, 
                   frame, 
                   corners):
        """Initialize template for hyperplane tracker.
        """
        self.frame = frame
        self.warp = utils.square_to_corners_warp(corners)     # Current warp
        # Sample template patch
        self.template = utils.sample_region(frame, 
                                            corners, 
                                            region_shape=self.config.REGION_SHAPE,
                                            Np=self.config.Np)
        self.template = utils.normalize_minmax(np.float32(self.template))

        # DEBUG: Some visualization here
        if self.config.DEBUG:
            # Record trajectories
            self._trajectories.append([self.warp])   # Store initial warp
            self._all_corners.append([corners])      # Store initial corners
            print('[DEBUG] corners:\n', corners)
            print('[DEBUG] warp:\n', self.warp)

            # Visualize template patch
            template_full = utils.sample_region(frame, 
                                                corners, 
                                                region_shape=self.config.REGION_SHAPE)
            template_full = utils.normalize_minmax(np.float32(template_full))

            plt.subplot(1,2,1)
            plt.imshow(self.template, cmap='gray')
            plt.title('Template\n' + str(self.template.shape[:2]))
            plt.subplot(1,2,2)
            plt.imshow(template_full, cmap='gray')
            plt.title('Template w/o subsampling\n'+ str(template_full.shape[:2]))
            plt.show()

        # Start synthesis now
        self.initialized = self._synthesis()

    def _synthesis(self):
        """Generate synthetic samples.
        """
        self.X, self.Y = [], []
        for motion_param in self.config.MOTION_PARAMS:
            sigma_d, sigma_t = motion_param
            warps = np.zeros((self.config.NUM_SYNTHESIS, 3, 3), dtype=np.float32)
            patches = np.zeros((self.config.NUM_SYNTHESIS, self.template.shape[0], self.template.shape[1]), dtype=np.float32)
            print('Generating {} synthetic samples...'.format(self.config.NUM_SYNTHESIS))
        
            for i in range(self.config.NUM_SYNTHESIS):
                # Generate random warp
                H = utils.random_hom(sigma_d, sigma_t)
                warps[i,:,:] = H
                disturbed_warp = np.matmul(self.warp, np.linalg.inv(H))     # Inverse warp
                disturbed_warp = utils.normalize_hom(disturbed_warp)

                # Grab the disturbed region and corners
                disturbed_corners = np.round(utils.apply_to_pts(disturbed_warp, utils._SQUARE)).astype(int)
                disturbed_template = utils.sample_region(self.frame, 
                                                         disturbed_corners,
                                                         region_shape=self.config.REGION_SHAPE,
                                                         Np=self.config.Np)
                disturbed_template = utils.normalize_minmax(np.float32(disturbed_template))
                patches[i,:,:] = disturbed_template

            # Prepare synthetic samples for learning
            X = (patches - np.expand_dims(self.template, axis=0)).reshape(-1, self.config.Np)
            self.X.append(X)
            self.Y.append(warps.reshape(-1, 9)[:,:-1])
        
        print('Synthesis done.')

        # Train now
        self._train()

        return True

    def _train(self):
        """Linear regression. 
        """
        self.learners = []
        # Calculate weight matrix per motion param
        for i in range(len(self.config.MOTION_PARAMS)):
            learner = linear_model.Ridge(alpha=self.config.LAMBD).fit(self.X[i], self.Y[i])
            self.learners.append(learner)
        print('Training done')
        return

    def update(self, 
               frame):
        """Produce updated tracked region.
        """
        if not self.initialized:
            raise Exception('Tracker uninitialized!')
        
        for _ in range(self.config.MAX_ITER):
            # Acquire current patch
            curr_corners = np.round(utils.apply_to_pts(self.warp, utils._SQUARE)).astype(int)
            curr_patch = utils.sample_region(frame, 
                                             curr_corners,
                                             region_shape=self.config.REGION_SHAPE,
                                             Np=self.config.Np)
            curr_patch = utils.normalize_minmax(np.float32(curr_patch))

            # Linear Rregression
            deltaI = np.expand_dims((curr_patch - self.template).reshape(-1), axis=0)

            # Greedy search, use the update with the maximum similarity score
            scores = []
            candidates = []
            for learner in self.learners:
                # Produce updating candidates
                p = learner.predict(deltaI).squeeze(0)
                update_warp = utils.make_hom(p)

                # Candidate updated warp
                candidate_warp = np.matmul(self.warp, update_warp)
                candidate_warp = utils.normalize_hom(candidate_warp)

                # Get candidate patch
                candidate_corners = np.round(utils.apply_to_pts(candidate_warp, utils._SQUARE)).astype(int)
                candidate_patch = utils.sample_region(frame, 
                                                      candidate_corners, 
                                                      region_shape=self.config.REGION_SHAPE,
                                                      Np=self.config.Np)
                candidate_patch = utils.normalize_minmax(np.float32(candidate_patch))

                # Image similarity score
                score = np.sum(np.square(candidate_patch - self.template))
                scores.append(score)
                candidates.append(update_warp)

            # Get minimum score
            idx = scores.index(min(scores))
            update_warp = candidates[idx]

            # Update
            self.warp = np.matmul(self.warp, update_warp)
            self.warp = utils.normalize_hom(self.warp)

        return np.round(utils.apply_to_pts(self.warp, utils._SQUARE)).astype(int)