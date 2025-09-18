from jinja2 import Template


class SlideTemplate:
    TEMPLATES: dict = dict(
        page="""
<!doctype html>
<html lang="en">
	<head>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <script src="https://cdn.bokeh.org/bokeh/release/bokeh-3.8.0.min.js"></script>
    <script src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-3.8.0.min.js"></script>
    <script src="https://cdn.bokeh.org/bokeh/release/bokeh-tables-3.8.0.min.js"></script>
    <script src="https://cdn.bokeh.org/bokeh/release/bokeh-gl-3.8.0.min.js"></script>
    <script src="https://cdn.bokeh.org/bokeh/release/bokeh-mathjax-3.8.0.min.js"></script>

		<title>reveal.js</title>

		<link rel="stylesheet" href="dist/reset.css">
		<link rel="stylesheet" href="dist/reveal.css">
		<link rel="stylesheet" href="dist/theme/black.css">

		<!-- Theme used for syntax highlighted code -->
		<link rel="stylesheet" href="plugin/highlight/monokai.css">
	</head>
	<body>
		<div class="reveal">
			<div class="slides">
				{{sections}}
			</div>
		</div>

		<script src="dist/reveal.js"></script>
		<script src="plugin/notes/notes.js"></script>
		<script src="plugin/markdown/markdown.js"></script>
		<script src="plugin/highlight/highlight.js"></script>
		<script>
			// More info about initialization & config:
			// - https://revealjs.com/initialization/
			// - https://revealjs.com/config/
			Reveal.initialize({
				hash: true,
				width: 1720,
  				eight: 720,
                autoSlide: 5000,
                loop: true,

				// Learn about plugins: https://revealjs.com/plugins/
				plugins: [ RevealMarkdown, RevealHighlight, RevealNotes ]
			});
		</script>
	</body>
</html>
        """,
        cover="""
<section>
  <h3>{{title | default('my ppt')}}</h3>
  <p>Presented by Eric</p>
  <p>{{content | default('2015-01-01')}} </p>
</section>
        """,
        content="""
<section>
  <h3>{{title | default('title')}}</h3>
  <p>
    {{content | default('content')}}
  </p>
</section>
        """,
        img="""
<section>
  <h3>{{title | default('title')}}</h3>
  <img class="r-stretch" src="{{content | default('img.png')}}" alt="">
</section>
        """,
        bokeh_plot="""
<section>
  <h3>{{title | default('title')}}</h3>
  {{content[0] | default('script')}}
  <div style="display: flex; justify-content: center; height: 100vh;">
  {{content[1] | default('div')}}
  </div>
</section>
        """,
        cards="""
<section>
  <h3>{{ title | default('Title') }}</h3>
  
  {# 卡片容器，使用Flex布局实现横向居中且可折行排列 #}
  <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; margin-top: 20px;">
    {% if content is defined and content is not none %}
      {% for index, value in content.items() %}
      {# 单个卡片 #}
      <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 16px; min-width: 150px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h4 style="margin: 0 0 10px 0; color: #333;">{{ index }}</h4>
        <p style="margin: 0; color: #666;">{{ value }}</p>
      </div>
      {% endfor %}
    {% else %}
      {# 当series未定义或为空时显示提示信息 #}
      <p>No data available</p>
    {% endif %}
  </div>
</section>
        """,
    )

    @classmethod
    def render_slide(cls, slide_data) -> str:
        """获取模板并渲染

        Args:
            template_name (str): 模板名称
            context (list): list of 渲染模板所需的上下文变量字典

        Returns:
            str: 渲染后的HTML字符串
        """
        template_str = cls.TEMPLATES.get(slide_data["template"], "content")

        slide_template = Template(template_str)  # type: ignore
        html = slide_template.render(
            title=slide_data["title"], content=slide_data["content"]
        )

        return html

    @classmethod
    def render_page(cls, sections):
        """渲染页面

        Args:
            sections (list): list of 渲染模板所需的html列表

        Returns:
            str: 渲染后的HTML字符串
        """
        page = "\n".join(sections)

        page_template = Template(cls.TEMPLATES.get("page"))
        return page_template.render(sections=page)
