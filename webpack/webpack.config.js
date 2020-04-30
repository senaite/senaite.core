const makeConfig = require("sc-recipe-staticresources");

module.exports = makeConfig(
  // name
  "senaite.core",

  // shortName
  "senaite",

  // path
  `${__dirname}/../src/senaite/core/browser/static`,

  //publicPath
  "++plone++senaite.core.static/",

);
