# vid-query
This is our project for an 8 week bootcamp on Generative AI, where we plan to combine the power of Retrieval Augmented Generation with the convenience of chrome extensions to solve an everyday problem related to YouTube videos. Our goal is to offer users an interactive experience that enhances their comfort while watching full-length YouTube videos in search of small pieces of information. Users will be able to chat with the vid-query bot and ask it questions about the video without having to navigate to a different app, or even a different tab. 

We believe that this extension will be incredibly useful for users who rely on YouTube videos for their learning. It will help them learn faster and save time with an extension that is efficient and easy to use.

## Setup Instructions:

### Chrome Extension (Frontend) Setup:
- Navigate to the chrome-extension folder and run the following commands
    - npm i
    - npm run build
- Open Google Chrome and navigate to:
    chrome://extensions/
- Toggle on Developer mode on the top right corner of the screen if toggled off 
- Click on 'Load Unpacked'
- Browse to the 'dist' folder in the vid-query/chrome-extension directory
- This will automatically add the extension to your Chrome browser.
- In case you want to make changes and reload:
    - Rerun: npm run build
    - Click on the Reload arrow in the vid-query Chrome extension card

### Backend Setup:
#### uv Installation
##### MacOs and Linux
`curl -LsSf https://astral.sh/uv/install.sh | less`
##### Windows
`powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
- Navigate to the backend folder and run the following commands:
    - `uv sync`
(Note: to do the above you must have Python installed which you can verify by running 'python3 --version')
- Add the .env file with your secrets configured according to the template in the .env.example file in the backend directory.
- Run the following command to start the server with hot reload (convenient for development):
    uvicorn app.main:app --reload
