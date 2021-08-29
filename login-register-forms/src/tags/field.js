const {html, importStyle, Element} = require('@beforesemicolon/html-plus');
const path = require('path');

class Field {
  defaultAttr = {
    name: 'field',
    type: 'text',
    label: 'Field',
    value: ''
  }
  
  constructor(node) {
    this.node = node;
    this.label = this.node.getAttribute('label') || 'Field';
    this.input = new Element('input');
  
    for (let attribute of this.node.attributes) {
      if (attribute.name !== 'label') {
        this.input.setAttribute(attribute.name, attribute.value || this.defaultAttr[attribute.name])
      }
    }
  }
  
  static get style() {
    return importStyle(path.resolve(__dirname, './field.scss'))
  }
  
  render() {
    return html(`
      <label class="field">
        <span>{label}</span>
        {input.outerHTML}
        {node.innerHTML}
      </label>
    `, this)
  }
}

module.exports.Field = Field;
