const LlamaOCR = require("llama-ocr");
const fs = require("fs");

// Get command-line arguments
const [filePath, apiKey, prompt] = process.argv.slice(2);

if (!filePath || !apiKey) {
  console.error("Usage: node ocrScript.js <filePath> <apiKey> [prompt]");
  process.exit(1);
}

async function runOCR() {
  try {
    console.log("Initializing OCR...");
    const ocr = new LlamaOCR(apiKey);

    console.log("Reading image file...");
    const imageBuffer = fs.readFileSync(filePath);
    console.log("Image loaded successfully.");

    console.log("Performing OCR...");
    const ocrResult = await ocr.recognize(imageBuffer, { prompt });
    console.log("OCR Completed Successfully.");
    console.log("OCR Result:", ocrResult.text);
  } catch (error) {
    console.error("Error during OCR:", error.message);
    console.error(error.stack);
  }
}

runOCR();

