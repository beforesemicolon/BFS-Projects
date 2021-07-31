const {Field} = require('./src/tags/field');
const {FormPageHeader} = require('./src/tags/formPageHeader');

const env = process.env.NODE_ENV || 'development';

module.exports = {
  env,
  customTags: [
    Field, FormPageHeader
  ]
}
