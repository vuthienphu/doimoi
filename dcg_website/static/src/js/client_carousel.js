/** @odoo-module **/

function initializeClientCarousels() {
    document.querySelectorAll('[data-client-carousel]').forEach((carousel) => {
        if (carousel.dataset.initialized === '1') return;
        carousel.dataset.initialized = '1';

        const viewport = carousel.querySelector('.client-carousel__viewport');
        const previous = carousel.querySelector('.client-carousel__control--prev');
        const next = carousel.querySelector('.client-carousel__control--next');
        if (!viewport || !previous || !next) return;

        const scrollPage = (direction) => {
            viewport.scrollBy({left: direction * viewport.clientWidth, behavior: 'smooth'});
        };
        previous.addEventListener('click', () => scrollPage(-1));
        next.addEventListener('click', () => scrollPage(1));
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeClientCarousels);
} else {
    initializeClientCarousels();
}
