// static/lookup/js/weather_result_slideshow.js
document.addEventListener('DOMContentLoaded', function() {
    const slideElements = [
        document.getElementById('bg-image-slot-1'),
        document.getElementById('bg-image-slot-2')
    ];

    // This script expects weather_result.html to create a global variable `weatherSpecificImages`
    if (!slideElements[0] || !slideElements[1] || 
        typeof weatherSpecificImages === 'undefined' || !Array.isArray(weatherSpecificImages) || weatherSpecificImages.length === 0) {
        console.error('Background slide elements or weatherSpecificImages array not found/empty for slideshow on weather_result page.');
        // Fallback to a very generic single image or just ensure content is visible
        if(slideElements[0]) slideElements[0].style.opacity = 0; // Hide if broken
        if(slideElements[1]) slideElements[1].style.opacity = 0; // Hide if broken
        return;
    }

    let currentImageIndex = 0; 
    let currentSlotIndex = 0;  

    // Set initial image
    slideElements[currentSlotIndex].style.transition = 'none'; 
    slideElements[currentSlotIndex].style.backgroundImage = `url('${weatherSpecificImages[currentImageIndex]}')`;
    slideElements[currentSlotIndex].style.opacity = 1;
    
    slideElements[(currentSlotIndex + 1) % 2].style.opacity = 0; // Ensure other slot is hidden
    
    setTimeout(() => { 
        slideElements[0].style.transition = 'opacity 1.2s cubic-bezier(.4,0,.2,1)';
        slideElements[1].style.transition = 'opacity 1.2s cubic-bezier(.4,0,.2,1)';
    }, 50);

    let loadedImagesCount = 0;
    let slideshowStarted = false;
    
    function attemptToStartSlideshow() {
        if (slideshowStarted) return;
        
        if (weatherSpecificImages.length <= 1) {
            console.log("Weather slideshow not started: 0 or 1 image for current weather.");
            // Ensure the single image is displayed if not already (it should be by initial setup)
            return;
        }
        
        slideshowStarted = true;
        console.log("Weather-specific slideshow started with cross-fade.");
        setInterval(function() {
            currentImageIndex = (currentImageIndex + 1) % weatherSpecificImages.length;
            changeImage(currentImageIndex);
        }, 5000); // Changed interval to 5s for this slideshow
    }
    
    weatherSpecificImages.forEach(src => {
        const img = new window.Image();
        img.onload = () => { 
            loadedImagesCount++; 
            if (loadedImagesCount === weatherSpecificImages.length) {
                attemptToStartSlideshow(); 
            }
        };
        img.onerror = () => { 
            loadedImagesCount++; 
            if (loadedImagesCount === weatherSpecificImages.length) {
                attemptToStartSlideshow(); 
            }
            console.warn(`Failed to load image for weather slideshow: ${src}`);
        };
        img.src = src;
    });
    
    setTimeout(attemptToStartSlideshow, 3000); // Fallback timer

    function changeImage(nextImageIndex) {
        const nextSlotIndex = (currentSlotIndex + 1) % 2; 

        const currentSlideElement = slideElements[currentSlotIndex];
        const nextSlideElement = slideElements[nextSlotIndex];

        nextSlideElement.style.backgroundImage = `url('${weatherSpecificImages[nextImageIndex]}')`;
        nextSlideElement.style.opacity = 1;
        currentSlideElement.style.opacity = 0;
        currentSlotIndex = nextSlotIndex;
    }
});