Instructions:
- Run 'main.py' to begin program
    - Pygame and Cython required
    - Written with Python 3.7.2, Pygame 1.9.4, Cython 0.29.3, untested in other versions
- Scroll to switch between 4 available tools
- Four available tools are:
    1) Set displacement
        - Left mouse button to displace positive (red)
        - Right mouse button to displace negative (blue)
    2) Set mask
        - Left mouse button to mask area (disable cells)
        - Right mouse button to unmask area (enable cells)
    3) Set wave speed
        - Left mouse button to set wave speed
        - Right mouse button to unset (restore to default) wave speed
        - '-' and '=' keys to increase and decrease value to set to
    3) Set damping
        - Left mouse button to set damping
        - Right mouse button to unset (reset to 0) wave speed
        - '-' and '=' keys to increase and decrease value to set to
- CTRL + scroll to change brush size
- CTRL + drag to select in a straight line
- SHIFT + drag to select zone
- 'C' key to clear all waves
- 'R' key to reset all, including waves, masking, speed and damping settings
- 'B' key to toggle blurring
- ESC key to cancel line or zone selection
- SPACE key to pause