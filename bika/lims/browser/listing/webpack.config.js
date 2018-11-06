const path = require('path');
const webpack = require('webpack');

module.exports = {
  entry: {
    listing: path.resolve(__dirname, './src/listing.coffee')
  },
  output: {
    filename: 'senaite.core.[name].js',
    path: path.resolve(__dirname, './static/js')
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx|coffee)$/,
        exclude: [/node_modules/],
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['react', 'es2015', 'es2016', 'env'],
            plugins: ['transform-class-properties']
          }
        }
      }, {
        test: /\.coffee$/,
        exclude: [/node_modules/],
        use: [
          {
            loader: 'coffee-loader',
            options: {}
          }
        ]
      }, {
        test: /\.css$/,
        use: [
          {
            loader: 'style-loader'
          },
          {
            loader: 'css-loader'
          }
        ]
      }
    ]
  },
  plugins: [
    // https://webpack.js.org/plugins/provide-plugin/
    new webpack.ProvidePlugin({
    })
  ],
  externals: {
    // https://webpack.js.org/configuration/externals
  }
};
