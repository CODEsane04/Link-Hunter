const express = require('express');
const { spawn } = require('child_process');
const { log } = require('console');
const router = express.Router();

//define the POST endpoint

router.post('/get-url', (req, res) => {
    // Get the image URL from the request body sent by the extension
    const { imageUrl } = req.body;

    if (!imageUrl) {
        return res.status(400).json({ error: 'No image URL provided' });
    }

    console.log("recieved image url : ", imageUrl);

    // Spawn a Python child process
    // The first argument is 'python' or 'python3'
    // The second is an array containing the script path and any arguments
    const Python_process = spawn('python3', ['../python_scripts/find_links.py', imageUrl]);

    let result_data = '';
    let error_data = '';

    // Listen for data coming from the Python script's standard output
    Python_process.stdout.on('data', (data) => {
        result_data += data.toString();
    });

    // Listen for any errors from the Python script
    Python_process.stderr.on('error', (error) => {
        error_data += error.toString();
    });

    //when the python script finishes
    Python_process.on('close', (code) => {
        if (code !== 0 || error_data) {
            console.log(`Python script error : ${error_data}`);
            res.status(500).json({error : 'failed to process the image'});
        }

        try {
            //parse the json script recieved from he python
            const results = JSON.parse(result_data);
            //send parse results back to extension
            
        } catch (error) {
            
        }
    })
    
})