---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: default
---

<h1>Agent Catalog</h1>

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
