---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults
title: Agent Economy
layout: default
---

<h2>What is Agent Economy</h2>
<p>I first heard this term in <a href="https://www.youtube.com/watch?v=v9JBMnxuPX8&t=12s">Sequoia AI Ascent 2025 Keynote.</a></p>

<p>
  <img src="/assets/figure.png" />
</p>

<p>Here is how they described it.</p>
<p class="highlight">An agent economy is one in which agents don't just communicate information. They transfer resources. The can make transactions. They keep track of each other. They understand trust and reliability. And they actually have their own economy. This economy doesn't cut out humans. It's all about humans. The agents work with the people and the people work with the agents, in this agent economy.</p>
<p>The idea strikes me. And I'd like to record our steps towards the agent economy on this website.</p>

<!-- <h2>AI Agent</h2>
<p>There are many definitions of <em>agent</em>.</p>

<p><a href="https://www.anthropic.com/engineering/building-effective-agents">Anthropic</a> categorize all variations as agentic systems, but draw an important architectural distinction between workflows and agents:</p>
<ul>
  <li>Workflows are systems where LLMs and tools are orchestrated through predefined code paths.</li>
  <li>Agents, on the other hand, are systems where LLMs dynamically direct their own processes and tool usage, maintaining control over how they accomplish tasks.</li>
</ul>

<p><a href="https://x.com/AndrewYNg/status/1801295202788983136">Andrew Ng</a> thinks the same way: "Rather than arguing over which work to include or exclude as being a true agent, we can acknowledge that there are different degrees to which systems can be agentic. "</p>

<p>ChatGPT summarizes all these into an abstract form: AI Agent – An autonomous computational entity that continuously <b>perceives</b> its environment, <b>updates</b> an internal state, <b>decides</b> (via reasoning, planning, or learned policy) which action to take, and executes that action in order to <b>maximize a defined objective</b> (utility, reward, or set of constraints).</p>


<h2>Research</h2>
<dl>
  <dt><a href="https://arxiv.org/abs/2505.15799">The Agentic Economy</a> by Microsoft Research</dt>
  <dd>We explore the implications of an agentic economy, where assistant agents act on behalf of consumers and service agents represent businesses, interacting programmatically to facilitate transactions. A key distinction we draw is between unscripted interactions — enabled by technical advances in natural language and protocol design — and unrestricted interactions, which depend on market structures and governance. </dd>
</dl> -->





<h2>General</h2>
<ul>
{% for agent in site.data.agents.general %}
  <li>
    <a href="{{ agent.url }}" target="_blank">{{ agent.name }}</a>
  </li>
{% endfor %}
</ul>

<h2>Finance</h2>
<ul>
{% for agent in site.data.agents.finance %}
  <li>
    <a href="{{ agent.url }}" target="_blank">{{ agent.name }}</a>
  </li>
{% endfor %}
</ul>

<h2>Coding</h2>
<ul>
{% for agent in site.data.agents.coding %}
  <li>
    <a href="{{ agent.url }}" target="_blank">{{ agent.name }}</a>
  </li>
{% endfor %}
</ul>
