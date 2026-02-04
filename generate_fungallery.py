import os
import random

# Source folders with images (add as many as you want!)
source_folders = [
    'play/photos',
    'portfolio',
    # Add more folders here
]

# Where to save the gallery HTML
output_folder = 'play'

def generate_gallery():
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp')
    all_images = []
    
    # Scan all folders recursively for images
    print("Scanning folders for images (including subfolders)...")
    for folder in source_folders:
        if os.path.exists(folder):
            # Walk through folder and all subfolders
            for root, dirs, files in os.walk(folder):
                for filename in files:
                    if filename.lower().endswith(image_extensions):
                        # Full path to the image
                        full_path = os.path.join(root, filename)
                        # Relative path from the play folder
                        relative_path = os.path.relpath(full_path, output_folder)
                        all_images.append(relative_path)
                        print(f"  Found: {filename} in {root}")
        else:
            print(f"  ⚠️  Folder not found: {folder}")
    
    # RANDOMIZE THE ORDER! 🎲
    random.shuffle(all_images)
    
    print(f"\nFound {len(all_images)} images total!")
    
    html = '''<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body {
            margin: 0;
            padding: 40px;
            background: #f0f0f0;
            display: flex;
            justify-content: center;
            touch-action: none;
        }
        .gallery-container {
            position: relative;
            max-width: 1400px;
            width: 100%;
        }
        
        .image-wrapper {
            position: absolute;
            border: 2px solid transparent;
            transition: border-color 0.2s;
        }
        
        .image-wrapper:hover {
            border-color: #ddd;
        }
        
        .image-wrapper.active {
            border-color: #666;
            z-index: 1000 !important;
        }
        
        .gallery-item {
            width: 100%;
            height: 100%;
            object-fit: contain;
            display: block;
            cursor: move;
            pointer-events: none;
        }
        
          
        .image-wrapper:hover .gallery-item {
            box-shadow: 0 4px 16px rgba(0,0,0,0.2);
        }
        
        .image-wrapper.dragging {
            opacity: 0.5;
        }
        
        /* Resize handle */
        .resize-handle {
            position: absolute;
            bottom: -5px;
            right: -5px;
            width: 20px;
            height: 20px;
            cursor: nwse-resize;
            opacity: 0;
            transition: opacity 0.2s;
        }
        
        
        .image-wrapper:hover .resize-handle,
        .image-wrapper.active .resize-handle {
            opacity: 1;
        }
        
        /* Fullscreen overlay */
        .fullscreen-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.7);
            z-index: 10000;
            cursor: pointer;
            align-items: center;
            justify-content: center;
        }
        .fullscreen-overlay.active {
            display: flex;
        }
        .fullscreen-overlay img {
            max-width: 95%;
            max-height: 95%;
            object-fit: contain;
            box-shadow: 0 0 50px rgba(0,0,0,0.5);
        }
        
        /* Instructions */
        .instructions {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: white;
            padding: 10px 20px;
            border-radius: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            font-size: 14px;
            z-index: 5000;
        }
    </style>
</head>
<body>
    <div class="instructions">
        Drag to move • Drag corner to resize • Double-tap for fullscreen
    </div>
    
    <div class="gallery-container" id="gallery">
'''
    
    # Create a tighter packed layout centered in the middle
    columns = 5
    column_positions = [0] * columns  # Track height of each column
    column_width = 270  # 250px image + 20px gap
    
    for i, img_path in enumerate(all_images):
        # Find the shortest column
        shortest_col = column_positions.index(min(column_positions))
        
        x_position = shortest_col * column_width
        y_position = column_positions[shortest_col]
        
        # Update column height (estimate - will be adjusted by actual image height)
        column_positions[shortest_col] += 280  # Average height + gap
        
        # Use forward slashes for web paths
        web_path = img_path.replace('\\', '/')
        html += f'''        <div class="image-wrapper" style="left: {x_position}px; top: {y_position}px; width: 250px; height: 250px;" data-col="{shortest_col}">
            <img src="{web_path}" alt="{os.path.basename(img_path)}" class="gallery-item">
            <div class="resize-handle"></div>
        </div>
'''
    
    # Calculate container height
    max_height = max(column_positions)
    
    html += f'''    </div>
    
    <!-- Fullscreen overlay -->
    <div class="fullscreen-overlay" id="fullscreen">
        <img src="" alt="">
    </div>
    
    <script>
        const gallery = document.getElementById('gallery');
        const wrappers = document.querySelectorAll('.image-wrapper');
        const fullscreenOverlay = document.getElementById('fullscreen');
        const fullscreenImg = fullscreenOverlay.querySelector('img');
        
        // Set gallery height based on images
        gallery.style.minHeight = '{max_height}px';
        
        // Adjust positions after images load for better packing
        const columnHeights = [0, 0, 0, 0, 0];
        const columnWidth = 270;
        
        wrappers.forEach((wrapper, index) => {{
            const img = wrapper.querySelector('.gallery-item');
            const resizeHandle = wrapper.querySelector('.resize-handle');
            
            img.onload = function() {{
                const col = parseInt(wrapper.dataset.col);
                const aspectRatio = img.naturalWidth / img.naturalHeight;
                const height = 250 / aspectRatio;
                
                wrapper.style.top = columnHeights[col] + 'px';
                wrapper.style.height = height + 'px';
                columnHeights[col] += height + 20;
                
                // Update gallery height
                const maxHeight = Math.max(...columnHeights);
                gallery.style.minHeight = maxHeight + 'px';
            }};
            
            let isDragging = false;
            let isResizing = false;
            let hasMoved = false;
            let offsetX, offsetY;
            let startX, startY, startWidth, startHeight;
            let lastTap = 0;
            
            // Touch support for pinch zoom
            let initialDistance = 0;
            let initialWidth = 0;
            
            // Dragging
            wrapper.addEventListener('mousedown', (e) => {{
                if (e.target === resizeHandle) return;
                isDragging = true;
                hasMoved = false;
                wrapper.classList.add('dragging');
                wrapper.classList.add('active');
                offsetX = e.clientX - wrapper.offsetLeft;
                offsetY = e.clientY - wrapper.offsetTop;
                wrapper.style.zIndex = 1000;
                e.preventDefault();
            }});
            
            wrapper.addEventListener('touchstart', (e) => {{
                if (e.target === resizeHandle) return;
                
                // Double-tap detection
                const currentTime = new Date().getTime();
                const tapLength = currentTime - lastTap;
                if (tapLength < 300 && tapLength > 0) {{
                    // Double tap - show fullscreen
                    fullscreenImg.src = img.src;
                    fullscreenOverlay.classList.add('active');
                    e.preventDefault();
                    return;
                }}
                lastTap = currentTime;
                
                if (e.touches.length === 2) {{
                    // Two finger pinch to zoom
                    const touch1 = e.touches[0];
                    const touch2 = e.touches[1];
                    initialDistance = Math.hypot(
                        touch2.clientX - touch1.clientX,
                        touch2.clientY - touch1.clientY
                    );
                    initialWidth = wrapper.offsetWidth;
                    wrapper.classList.add('active');
                }} else if (e.touches.length === 1) {{
                    // Single finger drag
                    isDragging = true;
                    hasMoved = false;
                    wrapper.classList.add('dragging');
                    wrapper.classList.add('active');
                    const touch = e.touches[0];
                    offsetX = touch.clientX - wrapper.offsetLeft;
                    offsetY = touch.clientY - wrapper.offsetTop;
                    wrapper.style.zIndex = 1000;
                }}
            }});
            
            // Resize handle
            resizeHandle.addEventListener('mousedown', (e) => {{
                isResizing = true;
                wrapper.classList.add('active');
                startX = e.clientX;
                startY = e.clientY;
                startWidth = wrapper.offsetWidth;
                startHeight = wrapper.offsetHeight;
                wrapper.style.zIndex = 1000;
                e.stopPropagation();
                e.preventDefault();
            }});
            
            resizeHandle.addEventListener('touchstart', (e) => {{
                isResizing = true;
                wrapper.classList.add('active');
                const touch = e.touches[0];
                startX = touch.clientX;
                startY = touch.clientY;
                startWidth = wrapper.offsetWidth;
                startHeight = wrapper.offsetHeight;
                wrapper.style.zIndex = 1000;
                e.stopPropagation();
                e.preventDefault();
            }});
            
            document.addEventListener('mousemove', (e) => {{
                if (isDragging) {{
                    hasMoved = true;
                    wrapper.style.left = (e.clientX - offsetX) + 'px';
                    wrapper.style.top = (e.clientY - offsetY) + 'px';
                }} else if (isResizing) {{
                    const deltaX = e.clientX - startX;
                    const newWidth = Math.max(100, startWidth + deltaX);
                    const aspectRatio = img.naturalWidth / img.naturalHeight;
                    const newHeight = newWidth / aspectRatio;
                    
                    wrapper.style.width = newWidth + 'px';
                    wrapper.style.height = newHeight + 'px';
                }}
            }});
            
            document.addEventListener('touchmove', (e) => {{
                if (e.touches.length === 2 && initialDistance > 0) {{
                    // Pinch zoom
                    const touch1 = e.touches[0];
                    const touch2 = e.touches[1];
                    const currentDistance = Math.hypot(
                        touch2.clientX - touch1.clientX,
                        touch2.clientY - touch1.clientY
                    );
                    const scale = currentDistance / initialDistance;
                    const newWidth = Math.max(100, initialWidth * scale);
                    const aspectRatio = img.naturalWidth / img.naturalHeight;
                    const newHeight = newWidth / aspectRatio;
                    
                    wrapper.style.width = newWidth + 'px';
                    wrapper.style.height = newHeight + 'px';
                    e.preventDefault();
                }} else if (isDragging && e.touches.length === 1) {{
                    hasMoved = true;
                    const touch = e.touches[0];
                    wrapper.style.left = (touch.clientX - offsetX) + 'px';
                    wrapper.style.top = (touch.clientY - offsetY) + 'px';
                }}
            }});
            
            document.addEventListener('mouseup', () => {{
                if (isDragging) {{
                    isDragging = false;
                    wrapper.classList.remove('dragging');
                    wrapper.classList.remove('active');
                    wrapper.style.zIndex = 1;
                }} else if (isResizing) {{
                    isResizing = false;
                    wrapper.classList.remove('active');
                    wrapper.style.zIndex = 1;
                }}
            }});
            
            document.addEventListener('touchend', () => {{
                isDragging = false;
                isResizing = false;
                initialDistance = 0;
                wrapper.classList.remove('dragging');
                wrapper.classList.remove('active');
                wrapper.style.zIndex = 1;
            }});
            
            // Double-click for fullscreen (desktop)
            wrapper.addEventListener('dblclick', (e) => {{
                if (!hasMoved) {{
                    fullscreenImg.src = img.src;
                    fullscreenOverlay.classList.add('active');
                }}
            }});
        }});
        
        // Click overlay to close fullscreen
        fullscreenOverlay.addEventListener('click', () => {{
            fullscreenOverlay.classList.remove('active');
        }});
        
        // Press Escape to close fullscreen
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'Escape') {{
                fullscreenOverlay.classList.remove('active');
            }}
        }});
    </script>
</body>
</html>'''
    
    output_path = os.path.join(output_folder, 'gallery.html')
    with open(output_path, 'w') as f:
        f.write(html)
    
    print(f"\n✅ Generated gallery with {len(all_images)} images!")
    print(f"📁 Gallery saved to: {output_path}")

generate_gallery()