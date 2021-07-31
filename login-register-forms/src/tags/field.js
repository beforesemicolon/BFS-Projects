const {composeTagString, importStyle} = require('@beforesemicolon/html-plus');
const path = require('path');

class Field {
  constructor(node) {
    this.attr = {
      name: 'field',
      type: 'text',
      label: 'Field',
      value: '',
      ...node.attributes
    }
    this.extraContent = node.renderChildren();
  }
  
  static get style() {
    return importStyle(path.resolve(__dirname, './field.scss'))
  }
  
  render() {
    const {label, ...attributes} = this.attr;
    
    return `
      <label class="field">
        <span>${label}</span>
        ${composeTagString({tagName: 'input', attributes})}
        ${this.extraContent}
      </label>
    `
  }
}

module.exports.Field = Field;
