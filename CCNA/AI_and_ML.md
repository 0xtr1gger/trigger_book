---
created: 2025-10-31 09:30:00
tags:
  - AI
---
## AI

>**AI (Artificial Intelligence)** refers to the capability of computers to simulate intelligence, which allows them to exhibit behavior typically associated with humans, such as learning, reasoning, recognizing patterns, problem-solving, and making decisions.

>[!example]+ Examples of AI
> - **Virtual assistants** (e.g., Siri, Alexa, Google Assistant).
> - **Recommendation systems** (e.g., Netflix, YouTube, Amazon product recommendations).
> - **Self-driving cars and robotics** (e.g., Tesla FSD, Waymo).
> - **Chat bots** (e.g., ChatGPT, virtual concierges).
> - **Game play and analysis** (e.g., Stockfish (chess), AlphaGo (Go)).
> - etc.
## ML

>**ML (Machine Learning)** is a subset of AI that focuses on developing algorithms that allow computers to learn from and make decisions/predictions based on data, without requiring explicit programming. 

- Instead of hard-coded instructions programmed by a human, ML algorithms identify patterns in data and made predictions or decisions based on those patterns.

>[!example]+ Examples of ML
>- **Email spam filtering**
>- **Personalized product recommendations**
>- **Fraud detection** (banking)
>- **Natural Language Processing (NLP)**
>- etc.

There are four main types of ML (not a comprehensive list):

- **Supervised learning**
	- The model is trained on labeled data, where the correct answers are provided, to make predictions on or classifications of new data. 

- **Unsupervised learning**
	- The model is given unlabeled data and tasked with finding patterns, relationships, or groupings withing the data.

- **Reinforcement learning** (trial-and-error)
	- The model learns by interacting with an environment, receiving rewards or penalties based on its actions to maximize its performance over time.

- **Deep learning** (inspired by the human brain)
	- A specialized subset of ML that uses multi-layered neural networks to handle large datasets and perform complex tasks like image recognition and natural language processing.
### Supervised learning

- **Supervised learning** trains a model on a labeled dataset.
	- Each input provided to the model for training has a corresponding label. 
	- By examining these labeled examples, the model learns the relationship between the data and the given label.
	- By training on labeled examples, the model learns to classify new, unseen data with high accuracy.

- **Advantages:**
	- Highly accurate when labeled data is available, which can be expensive and time-consuming to create.
	- Straightforward to understand and implement.

- **Disadvantages:**
	- Requires large, labeled data sets.
	- Output is limited to the labels in the training data.
### Unsupervised learning

- **Unsupervised learning** trains the model on an unlabeled dataset.
	- No predefined labels are provided.
	- The model can discover patterns, structured, or relationships within the data (without human supervision).
		- If groups (clusters) similar data points based on shared features.

- **Advantages:**
	- No need for labeled data.
	- Reveals hidden patterns.

- **Disadvantages:**
	- Interpretation and labeling of the results is required.
	- Less accurate.
### Reinforcement learning

- **Reinforcement learning** trains a model by rewarding or penalizing its actions in a given environment to maximize its performance over time.
	- The model learns to take actions that achieve the highest reward or best outcome.

- The model, called an **agent**, interacts with an environment.
- It takes an action and receives feedback (reward or penalty).
- The agent uses this feedback to adjust this behavior and learn which actions lead to the best results.

- Applications:
	- **Self-driving cars:** Learning how to navigate safely by trial and error.
	- **Game AI:** Mastering strategies in games like Chess, Go, or video games.
	- **Robotics:** Teaching robots how to walk, pick up objects, or perform tasks.

- **Advantages:**
	- Capable of learning complex behaviors.
	- Adapts well to dynamic environments.

- **Disadvantages:**
	- Resource-intensive.
	- Risk of sub-optimal learning if the reward system isn't properly designed.
### Deep learning

- **Deep learning** uses artificial neural networks to process and learn large and complex datasets.
	- An *artificial neural network* is a computational model inspired by how biological neural networks like the human brain process information.
	- Data is passed through multiple layers of nodes (neurons), with each layer extracting increasingly abstract features.
	- The neural network can be trained using supervised, unsupervised, and/or reinforcement learning methods.

- **Advantages:**
	- Deep learning excels at handling large, unstructured datasets like images, audio, and text.
	- Achieves state-of-the-art performance in tasks like image recognition, natural language processing (NLP), and autonomous driving.

- **Disadvantages:**
	- Resource-intensive.
	- The model can be a "black box", making it difficult to interpret how it arrives at its decisions.

## Predictive and generative AI

- **Predictive AI**
	- Uses ML to analyze historical data and predict future outcomes or trends.
	- Examples include security anomaly detection and weather forecasting. 

- **Generative AI**
	- Uses ML to learn patterns from existing data and create new content, such as text, images, or audio.
	- Examples include ChatGPT, Gemini, Midjourney, DALL-E, etc.

### Predictive AI

- **Predictive AI** analyses historical data to forecast future outcomes, trends, or events.
- The model identifies patterns and correlations in past data and applies these patterns to make predictions.

- Applications:
	- **Healthcare:** Predicting patient outcomes or disease progression.
	- **Network security:** Detecting anomalies that might indicate a potential threat or failure.
	- **Traffic management:** Predicting congestion based on historical and real-time traffic data.
	- **Business forecasting:** Predicting sales trends or customer behavior.
	- **Weather forecasting:** Analyzing meteorological data to predict weather conditions.

- **Advantages:**
	- Improves decision-making by providing actionable insights.
	- Detects potential problems before they occur (e.g., network issues or severe weather).

- **Disadvantages:**
	- Requires high-quality, relevant historical data.
	- Accuracy depends on how well the patterns in past data generalize to new scenarios.

### Generative AI

- **Generative AI** learns patterns from existing data and creates new content such as text, images, and audio.
- It focuses on producing outputs that resemble the input that it was trained on.

- Applications
	- **Text generation:** ChatGPT, Gemini, Copilot, etc. (LLMs).
	- **Image generation:** Midjourney, DALL-E.
	- **Video generation:** Sora (OpenAI), Veo 2 (Google).

- **Advantages:**
	- Great for creative tasks where human input is limited or time-consuming.
	- Enables automation of content creation across various fields.

- **Disadvantages:**
	- Risk of misuse (e.g., deep fakes, plagiarism).
	- Generated content is only as good as the quality of the training material.
	- Hallucinations. 

### Predictive and generative AI in networks

- **Predictive AI:**
	- **Traffic forecasting:** Predict network traffic patterns to optimize bandwidth allocation and prevent congestion.
	- **Security threat detection:** Identify anomalies or suspicious patterns in real-time to mitigate potential security threats.
	- **Predictive maintenance:** Anticipate hardware failures by analyzing historical and current performance data to reduce downtime.

- **Generative AI:**
	- **Network documentation:** Generate documentation about network configurations, policies, etc.
	- **Configuration generation:** Automatically generate configurations for network devices based on desired policies and requirements.
	- **Network design:** Suggest optimized network layouts or modifications tailored to specific business needs and workloads.
	- **Troubleshooting:** Produce solutions or diagnostics based on log files or error messages to resolve issues efficiently. 
	- **Script generation:** Automatically generate network automation scripts (e.g., Python scripts to configure network devices).