const {importStyle} = require("@beforesemicolon/html-plus");
const path = require("path");

class FormPageHeader {
  constructor(node) {
    this.title = node.attributes.title ?? 'Form Page';
    this.link = node.attributes.link ?? null;
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
    return `
        <header class="form-page-header">
            <h2>${this.title}</h2>
            ${this.link && `<a href="${this.link.path}">${this.link.label}</a>`}
        </header>
    `;
  }
}

module.exports.FormPageHeader = FormPageHeader;
