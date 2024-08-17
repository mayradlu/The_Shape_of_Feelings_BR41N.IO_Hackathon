# The Shape of Feelings BR41N.IO Hackathon
## Project Overview
The Shape of Feelings is a project developed for a hackathon organized by Br4in.io, under the Programming & Arts Project category. The project aims to explore the intersection of neuroscience and art by using brain signals to visualize emotions in real-time.

## How it works

**Brainwave Data Capture**

The Unicorn Hybrid Black device is used to capture real-time brain signals from the user. The device monitors various channels and frequencies corresponding to different brainwave bands such as Theta, Alpha, Beta, and Gamma.

**Signal Processing**

The raw data is processed and filtered using various Python libraries such as socket, scipy, numpy, and matplotlib. A Butterworth bandpass filter is applied to the signals to remove noise and focus on the relevant frequency bands. The data is then visualized using periodograms to analyze the power spectral density (PSD) of the brainwave signals across the different frequency bands.

**Emotion Detection and Visualization**

The emotions detected from the brain signals are mapped to visual attributes using the following logic:
 * **Colors** Different colors are assigned based on the intensity of the Alpha band, which is often associated with relaxation and calmness.
* **Circle Size** The size of the circles in the visual representation is influenced by the Gamma band, typically associated with higher mental activity and arousal.

The visualization is created using the pygame library, where the circles' size and color dynamically change in response to the detected brainwave patterns. The final output is a constantly evolving visual representation of the user's emotional state.

<p align="center">
  <img src="https://github.com/user-attachments/assets/1eb1bce9-1c11-490c-b98b-c86edefea09d" alt="400" width="400">
</p>
