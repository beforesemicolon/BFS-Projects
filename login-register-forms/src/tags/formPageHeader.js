const {importStyle, html} = require("@beforesemicolon/html-plus");
const path = require("path");

class FormPageHeader {
  constructor(node) {
    this.title = node.getAttribute('title') ?? 'Form Page';
    this.link = node.getAttribute('link') ?? null;
  }
  
  static get customAttributes() {
    return {
      link: {execute: true}
    };
  }
  
  static get style() {
    return importStyle(path.resolve(__dirname, './formPageHeader.scss'))
  }
  
  render() {
    return html(`
        <header class="form-page-header">
            <h2>{title}</h2>
            <a #if="link" href="{link.path}">{link.label}</a>
        </header>
    `, this);
  }
}

module.exports.FormPageHeader = FormPageHeader;
