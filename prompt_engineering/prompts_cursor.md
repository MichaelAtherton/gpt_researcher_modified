# 1
I need you to put your investigative hat on. I have a directory in this ai research project that i need to understand. Here is the directory: /Users/michaelatherton/Documents/condaEnv/AIRL/personal_projects/gpt-researcher/gpt_researcher


Tell me your understanding of this directory and what each of the files do in this dir


# 2

######
# multi_agents

Ok, this is a good start. we need to go a step deeper and identify every prompt that, when edited, will affect the multi_agent behavior. 

you need to analyze each of the .py files in agents/ and: 
1. Identify each prompt
2. return the function with this prompt as a hyperlink
3. provide a description of the prompt
4. provide a short explination of how changing the prompt will affect the agents behavior. 

Before you start this analysis, give me your understanding of my objectives


######
# gpt_researcher

Ok, this is a good start. we need to go a step deeper and identify every prompt that, when edited, will affect the gpt_researcher behavior. 

You need to analyze each of the prompts in gpt_researcher/curent_topics_prompts.py and: 
1. Identify each prompt path ie. 'summary', 'detailed', 'deep research'
2. Identify prompts in each path
3. return the function with this prompt as a hyperlink
4. provide a description of the prompt
5. provide a short explination of how changing the prompt will affect the agents behavior.

Before you start this analysis, give me your understanding of my objectives
######


# 3
now, write this breakdown of all the prompts used in the multi-agent system to the file /Users/michaelatherton/Documents/condaEnv/AIRL/personal_projects/gpt-researcher/prompt_engineering/multi_agent.md

######
# gpt_researcher

Now, write this breakdown of all the prompts used in the gpt_researcher system to the file /Users/michaelatherton/Documents/condaEnv/AIRL/personal_projects/gpt-researcher/prompt_engineering/gpt_researcher.py

# 4 
# Do the same for the other project (OPTIONAL)
Now that we've identified the agents and prompt locations, we need to follow this process for the agent system in the /Users/michaelatherton/Documents/condaEnv/AIRL/personal_projects/gpt-researcher/gpt_researcher directory. 


# 5
Ok, now let's do something exciting and modify the behavior of the gpt_researcher system. 

*NOTE*
The ONLY thing we will be modifying are the prompts in current_topics_prompts.py. Do NOT edit any other sections or functions in the code. Do you understand? 


# 6

I'll start by describing the output I want and we can work backwards from there. 

Instead of generating reports I want the output to be linkedin posts examples. 

let's first identify which prompts we will need to modify this. We may need to check wtih main.py to identify the differrent system paths we can take. For example: we do not want to use 'deep research' as that would be overkill on the research side. 

Given my goals, what would be your first step? let's discuss before you change any code

######
# Daily Search

I'll start by describing the output I want and we can work backwards from there. 

Curently gpt_researcher generates one off reports. My goal is to create eaily reports on a specific topic. This search should only produce reports that contain up to date information. Because these reports are running daily, there is a risk of duplicate data. I need to obtain only  new information about the topic each day. This will allow the CEO of a company with actionable insights that will give him a competitive advantage over his competitors. 

In your own words, explain to me your understanding of my requirements 

######
You're understanding is 100% correct. 

Now, let's form some strategies on how to modify the gpt_researcher prompts in /Users/michaelatherton/Documents/condaEnv/AIRL/personal_projects/gpt-researcher/gpt_researcher/current_topics_prompts.py. Let's discuss the merits of using the summary, detailed and deep research paths. What capabilities and parmeters do each of these paths have that would lend themselfs to our goal? 
######

# 7 
let's continue with the plan you have laid out. Examine main.py


# 8 
The report type options I have are:
- 'Summary - Short and fast (~2min)'
- 'Detailed - In depth and longer (~5 min)'
- 'Resource Report'

Which of these options will use our new LinkedIn prompts?


RESPONSE:
#####################
1. The report types are defined in ReportType enum in gpt_researcher/utils/enum.py
2. The UI options you see are mapped in frontend/nextjs/components/Task/ResearchForm.tsx as:
   * "Summary - Short and fast (~2 min)" -> research_report
   * "Detailed - In depth and longer (~5 min)" -> detailed_report
   * "Deep Research Report" -> deep

######################
