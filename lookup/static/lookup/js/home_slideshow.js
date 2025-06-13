// static/lookup/js/home_slideshow.js
document.addEventListener('DOMContentLoaded', function() {
    const slideElements = [
        document.getElementById('bg-image-slot-1'),
        document.getElementById('bg-image-slot-2')
    ];

    // Ensure homeImages is defined and slide elements exist
    if (!slideElements[0] || !slideElements[1] || 
        typeof homeImages === 'undefined' || !Array.isArray(homeImages) || homeImages.length === 0) {
        console.error('Background slide elements or homeImages array not found/empty for slideshow.');
        if (!slideElements[0]) console.error  ('Could not find #bg-image-slot-1');
        if (!slideElements[1]) console.error  ('Could not find #bg-image-slot-2');
        return;
    }

    let currentImageIndex = 0; // Index for the homeImages array
    let currentSlotIndex = 0;  // Index for slideElements array (0 or 1)

    // Set initial image without transition on the first slot
    slideElements[currentSlotIndex].style.transition = 'none'; 
    slideElements[currentSlotIndex].style.backgroundImage = `url('${homeImages[currentImageIndex]}')`;
    slideElements[currentSlotIndex].style.opacity = 1;
    
    // Ensure the other slot is transparent and ready
    slideElements[(currentSlotIndex + 1) % 2].style.opacity = 0;
    
    // Restore transition for subsequent changes after a brief moment
    setTimeout(() => { 
        slideElements[0].style.transition = 'opacity 1.2s cubic-bezier(.4,0,.2,1)';
        slideElements[1].style.transition = 'opacity 1.2s cubic-bezier(.4,0,.2,1)';
    }, 50);


    let loadedImagesCount = 0;
    let slideshowStarted = false;
    
    function attemptToStartSlideshow() {
        if (slideshowStarted) return;
        
        if (homeImages.length <= 1) { // No slideshow for 0 or 1 image
            // Ensure the single image is displayed if not already
            if (homeImages.length === 1 && slideElements[currentSlotIndex].style.backgroundImage !== `url('${homeImages[0]}')`) {
                slideElements[currentSlotIndex].style.backgroundImage = `url('${homeImages[0]}')`;
                slideElements[currentSlotIndex].style.opacity = 1;
                slideElements[(currentSlotIndex + 1) % 2].style.opacity = 0;
            }
            console.log("Slideshow not started: 0 or 1 image.");
            return;
        }
        
        slideshowStarted = true;
        console.log("Slideshow started with cross-fade.");
        setInterval(function() {
            currentImageIndex = (currentImageIndex + 1) % homeImages.length;
            changeImage(currentImageIndex);
        }, 6000); // Interval for changing images
    }
    
    // Preload images
    homeImages.forEach(src => {
        const img = new window.Image();
        img.onload = () => { 
            loadedImagesCount++; 
            if (loadedImagesCount === homeImages.length) {
                console.log("All images preloaded for cross-fade.");
                attemptToStartSlideshow(); 
            }
        };
        img.onerror = () => { 
            loadedImagesCount++; 
            if (loadedImagesCount === homeImages.length) {
                attemptToStartSlideshow(); 
            }
            console.warn(`Failed to load image for cross-fade: ${src}`);
        };
        img.src = src;
    });
    
    // Fallback timer
    setTimeout(attemptToStartSlideshow, 3500); 

    function changeImage(nextImageIndex) {
        const nextSlotIndex = (currentSlotIndex + 1) % 2; // The slot that is currently hidden

        const currentSlideElement = slideElements[currentSlotIndex];
        const nextSlideElement = slideElements[nextSlotIndex];

        // 1. Set the new image on the hidden slot
        nextSlideElement.style.backgroundImage = `url('${homeImages[nextImageIndex]}')`;
        
        // 2. Fade in the next slot (which has the new image)
        nextSlideElement.style.opacity = 1;
        
        // 3. Simultaneously, fade out the current slot
        currentSlideElement.style.opacity = 0;

        // 4. Update currentSlotIndex to the slot that is now visible
        currentSlotIndex = nextSlotIndex;
    }
});