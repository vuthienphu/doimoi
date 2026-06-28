/** @odoo-module **/

import { LoadingIndicator } from "@web/webclient/loading_indicator/loading_indicator";
import { patch } from "@web/core/utils/patch";

// Configuration for different cat animations
const CAT_ANIMATIONS = {
    1: "ar_loading.CatLoadingIndicator1", // Rotating cat with detailed features
    2: "ar_loading.CatLoadingIndicator2"  // Segments cat animation
};

// Default cat animation (can be changed here)
// const DEFAULT_CAT = 2;

// You can also randomize the cat animation
const DEFAULT_CAT = Math.floor(Math.random() * Object.keys(CAT_ANIMATIONS).length) + 1;

// Patch the LoadingIndicator to use our custom cat template
patch(LoadingIndicator, {
    template: CAT_ANIMATIONS[DEFAULT_CAT]
});

// Override the template at the class level for better compatibility
LoadingIndicator.template = CAT_ANIMATIONS[DEFAULT_CAT];
