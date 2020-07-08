const path = require("path");
const webpack = require("webpack");
const childProcess = require("child_process");

const CopyPlugin = require("copy-webpack-plugin");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const { CleanWebpackPlugin } = require("clean-webpack-plugin");

const gitCmd = "git rev-list -1 HEAD -- `pwd`";
let gitHash = childProcess.execSync(gitCmd).toString().substring(0, 7);

const staticPath = path.resolve(__dirname, "../src/senaite/core/browser/static");

const devMode = process.env.NODE_ENV !== 'production';


module.exports = {
  context: path.resolve(__dirname, "app"),
  entry: {
    main: [
      // scripts
      "./senaite.core.js",
      // styles
      "./scss/senaite.core.scss",
    ],
  },
  output: {
    filename: `[name]-${gitHash}.js`,
    path: path.resolve(staticPath, "bundles"),
    publicPath: "/++plone++senaite.core.static/bundles"
  },
  module: {
    rules: [
      {
        // JS
        test: /\.(js|jsx)$/,
        exclude: [/node_modules/],
        use: [
          {
            // https://webpack.js.org/loaders/babel-loader/
            loader: "babel-loader"
          }
        ]
      },
      {
        // SCSS
        test: /\.s[ac]ss$/i,
        use: [
          {
            // https://webpack.js.org/plugins/mini-css-extract-plugin/
            loader: MiniCssExtractPlugin.loader,
            options: {
              hmr: process.env.NODE_ENV === "development"
            },
          },
          {
            // https://webpack.js.org/loaders/css-loader/
            loader: "css-loader"
          },
          {
            // https://webpack.js.org/loaders/sass-loader/
            loader: "sass-loader"
          }
        ]
      },
      {
        test: /\.(woff(2)?|ttf|eot|svg)(\?v=\d+\.\d+\.\d+)?$/,
        use: [
          {
            // https://webpack.js.org/loaders/file-loader/
            loader: "file-loader",
            options: {
              name: "[name].[ext]",
              outputPath: "../fonts",
              publicPath: "/++plone++senaite.core.static/fonts",
            }
          }
        ]
      },
      {
        test: /\.(png|jpg)(\?v=\d+\.\d+\.\d+)?$/,
        use: [
          {
            // https://webpack.js.org/loaders/file-loader/
            loader: "file-loader",
            options: {
              name: "[name].[ext]",
              outputPath: "../assets/img",
              publicPath: "/++plone++senaite.core.static/assets/img",
            }
          }
        ]
      }
    ]
  },
  plugins: [
    // https://github.com/johnagan/clean-webpack-plugin
    new CleanWebpackPlugin(),
    // https://webpack.js.org/plugins/html-webpack-plugin/
    new HtmlWebpackPlugin({
      inject: false,
      filename:  path.resolve(staticPath, "resources.pt"),
      template: "resources.pt",
    }),
    // https://webpack.js.org/plugins/mini-css-extract-plugin/
    new MiniCssExtractPlugin({
      filename: devMode ? "[name].css" : "[name].[hash].css",
      chunkFilename: devMode ? "[id].css" : "[id].[hash].css",
    }),
    // https://webpack.js.org/plugins/copy-webpack-plugin/
    new CopyPlugin({
      patterns: [
      { from: "../node_modules/jquery", to: path.resolve(staticPath, "lib/jquery") },
      { from: "../node_modules/jquery-form", to: path.resolve(staticPath, "lib/jquery-form") },
      { from: "../node_modules/jquery-migrate", to: path.resolve(staticPath, "lib/jquery-migrate") },
      { from: "../node_modules/jqueryui", to: path.resolve(staticPath, "lib/jqueryui") },
      { from: "../node_modules/jquery-ui-timepicker-addon", to: path.resolve(staticPath, "lib/jquery-ui-timepicker-addon") },
      { from: "../node_modules/bootstrap", to: path.resolve(staticPath, "lib/bootstrap") },
      { from: "../node_modules/bootstrap-confirmation2", to: path.resolve(staticPath, "lib/bootstrap-confirmation2") },
      { from: "../node_modules/popper.js", to: path.resolve(staticPath, "lib/popperjs") },
      { from: "../node_modules/react", to: path.resolve(staticPath, "lib/react") },
      { from: "../node_modules/react-dom", to: path.resolve(staticPath, "lib/react-dom") },
      { from: "../node_modules/tinymce", to: path.resolve(staticPath, "lib/tinymce") },
      { from: "../node_modules/@fortawesome", to: path.resolve(staticPath, "lib/@fortawesome") },
      ]
    }),
    // https://webpack.js.org/plugins/provide-plugin/
    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery",
      bootstrap: "bootstrap",
      tinyMCE: "tinymce"
    }),
  ],
  externals: {
    // https://webpack.js.org/configuration/externals
    react: "React",
    "react-dom": "ReactDOM",
    $: "jQuery",
    jquery: "jQuery",
    bootstrap: "bootstrap",
    tinyMCE: "tinymce"
  }
};
