# Image Relevance

AI Image Understanding & Content Matching Engine. Tags images with a vision model, matches them to blog posts by meaning, and rejects bad matches with an explanation

## Architecture

`TODO: Architecture Diagram`

## Setup

`TODO: Run steps `

## Limitations

**Gemini API Free Tier:** The vision pipeline, `app/vision.py` and `app/batch.py` is fully implemented with retries and rate-limit pacing to stay under the 15RPM range for 3.5 Flash-Lite. However, the Gemini API Free Tier is simply not sufficient to run the vision model on each of the 50 images in the dataset, and funding will be required to run. A cost tracking infrastructure has been implemented in `app/vision.py`, however it has not been verified against a Gemini API call.

My workaround was to pre-generate Metadata via Gemini Chat, and thus pasting in the given data into `data/metadata.json`, and will later be called.
