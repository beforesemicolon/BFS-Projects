const {composeTagString} = require('@beforesemicolon/html-plus');

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
