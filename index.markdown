---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: home
---

<h1>Agent Catalog</h1>

<h2>General</h2>
<ul>
{% for agent in site.data.agents.general %}
  <li>
    <img src="{{ agent.image }}" alt="{{ agent.name }}" style="width: 100px; height: auto;">
    <a href="{{ agent.url }}">{{ agent.name }}</a>
  </li>
{% endfor %}
</ul>

<h2>Finance</h2>
<ul>
{% for agent in site.data.agents.finance %}
  <li>
    <img src="{{ agent.image }}" alt="{{ agent.name }}" style="width: 100px; height: auto;">
    <a href="{{ agent.url }}">{{ agent.name }}</a>
  </li>
{% endfor %}
</ul>

<h2>Coding</h2>
<ul>
{% for agent in site.data.agents.coding %}
  <li>
    <img src="{{ agent.image }}" alt="{{ agent.name }}" style="width: 100px; height: auto;">
    <a href="{{ agent.url }}">{{ agent.name }}</a>
  </li>
{% endfor %}
</ul>
