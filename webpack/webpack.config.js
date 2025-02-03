const path = require("path");
const webpack = require("webpack");
const childProcess = require("child_process");

const BundleAnalyzerPlugin = require("webpack-bundle-analyzer").BundleAnalyzerPlugin;
const CleanCSS = require("clean-css");
const CopyPlugin = require("copy-webpack-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const MergeIntoSingleFilePlugin = require("webpack-merge-and-include-globally");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const TerserPlugin = require("terser-webpack-plugin");
const uglifyJS = require("uglify-js");
const { CleanWebpackPlugin } = require("clean-webpack-plugin");


const gitCmd = "git rev-list -1 HEAD -- `pwd`";
let gitHash = childProcess.execSync(gitCmd).toString().substring(0, 7);

const staticPath = path.resolve(__dirname, "../src/senaite/core/browser/static");

const devMode = process.env.mode == "development";
const prodMode = process.env.mode == "production";
const mode = process.env.mode;
console.log(`RUNNING WEBPACK IN '${mode}' MODE`);


module.exports = {
  // https://webpack.js.org/configuration/devtool
  devtool: devMode ? "eval" : "source-map",
  // https://webpack.js.org/configuration/mode/#usage
  mode: mode,
  context: path.resolve(__dirname, "app"),
  entry: {
    // https://webpack.js.org/configuration/entry-context/#entry-descriptor
    "senaite.core": [
      // scripts
      "./senaite.core.js",
      // styles
      "./scss/senaite.core.scss",
    ],
    "senaite.core.widgets": [
      // scripts
      "./senaite.core.widgets.js",
    ]
  },
  output: {
    filename: devMode ? "[name].js" : `[name]-${gitHash}.js`,
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
        test: /\.css$/,
        use: [
          {
            // https://webpack.js.org/plugins/mini-css-extract-plugin/
            loader: MiniCssExtractPlugin.loader,
          },
          {
            // https://webpack.js.org/loaders/css-loader/
            loader: "css-loader"
          },
        ]
      },
      {
        // SCSS
        test: /\.s[ac]ss$/i,
        use: [
          {
            // https://webpack.js.org/plugins/mini-css-extract-plugin/
            loader: MiniCssExtractPlugin.loader,
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
  optimization: {
    minimize: prodMode,
    minimizer: [
      // https://v4.webpack.js.org/plugins/terser-webpack-plugin/
      new TerserPlugin({
        exclude: /\/modules/,
        terserOptions: {
          // https://github.com/webpack-contrib/terser-webpack-plugin#terseroptions
          sourceMap: false, // Must be set to true if using source-maps in production
          format: {
            comments: false
          },
          compress: {
            drop_console: true,
            passes: 2,
          },
        }
      }),
      // https://webpack.js.org/plugins/css-minimizer-webpack-plugin/
      new CssMinimizerPlugin({
        exclude: /\/modules/,
        minimizerOptions: {
          preset: [
            "default",
            {
              discardComments: { removeAll: true },
            },
          ],
        },
      }),
    ],
  },
  plugins: [
    // https://github.com/johnagan/clean-webpack-plugin
    new CleanWebpackPlugin({
      verbose: false,
      // Workaround in `watch` mode when trying to remove the `resources.pt` in the parent folder:
      // Error: clean-webpack-plugin: Cannot delete files/folders outside the current working directory.
      cleanAfterEveryBuildPatterns: ["!../*"],
    }),
    // https://webpack.js.org/plugins/html-webpack-plugin/
    new HtmlWebpackPlugin({
      inject: false,
      filename:  path.resolve(staticPath, "resources.pt"),
      template: "resources.pt",
    }),
    new webpack.ProgressPlugin(),
    // https://github.com/webpack-contrib/webpack-bundle-analyzer
    // new BundleAnalyzerPlugin(),
    // https://github.com/markshapiro/webpack-merge-and-include-globally
    new MergeIntoSingleFilePlugin({
      files: [{
        src: [
          // legacy.js
          "../src/senaite/core/browser/static/js/bika.lims.analysisrequest.js",
          "../src/senaite/core/browser/static/js/bika.lims.artemplate.js",
          "../src/senaite/core/browser/static/js/bika.lims.batch.js",
          "../src/senaite/core/browser/static/js/bika.lims.bikasetup.js",
          "../src/senaite/core/browser/static/js/bika.lims.calculation.edit.js",
          "../src/senaite/core/browser/static/js/bika.lims.client.js",
          "../src/senaite/core/browser/static/js/bika.lims.common.js",
          "../src/senaite/core/browser/static/js/bika.lims.graphics.controlchart.js",
          "../src/senaite/core/browser/static/js/bika.lims.graphics.range.js",
          "../src/senaite/core/browser/static/js/bika.lims.instrument.js",
          "../src/senaite/core/browser/static/js/bika.lims.referencesample.js",
          "../src/senaite/core/browser/static/js/bika.lims.rejection.js",
          "../src/senaite/core/browser/static/js/bika.lims.site.js",
          "../src/senaite/core/browser/static/js/bika.lims.utils.attachments.js",
          "../src/senaite/core/browser/static/js/bika.lims.utils.barcode.js",
          "../src/senaite/core/browser/static/js/bika.lims.worksheet.js",
          "../src/senaite/core/browser/static/js/bika.lims.worksheet.print.js",
          "../src/senaite/core/browser/static/js/bika.lims.loader.js",
        ],
        dest: code => {
          if (devMode) {
            return {
              "legacy.js": code
            }
          }
          const min = uglifyJS.minify(code, {sourceMap: {
            filename: "legacy.js",
            // url: "legacy.js.map"
          }, compress: {drop_console: true}});
          return {
            "legacy.js":min.code,
            // "legacy.js.map": min.map
          }
        },
      }, {
        // legacy.css
        src: [
          "../src/senaite/core/browser/static/css/bika.lims.graphics.css",
        ],
        dest: code => ({
          "legacy.css":new CleanCSS({}).minify(code).styles,
        })
      }, {
        // thirdparty.js
        src: [
          "../src/senaite/core/browser/static/thirdparty/jqueryui/jquery-ui-1.12.1.min.js",
          "../src/senaite/core/browser/static/thirdparty/jqueryui/jquery-ui-i18n.min.js",
          "../src/senaite/core/browser/static/thirdparty/combogrid/jquery.ui.combogrid-1.6.4.js",
          "../src/senaite/core/browser/static/thirdparty/plone/overlayhelpers.js",
          "../src/senaite/core/browser/static/thirdparty/jquery-barcode-2.2.0.min.js",
          "../src/senaite/core/browser/static/thirdparty/jquery-qrcode-0.17.0.min.js",
          "../src/senaite/core/browser/static/thirdparty/d3.js",
        ],
        dest: code => {
          if (devMode) {
            return {
              "thirdparty.js": code
            }
          }
          const min = uglifyJS.minify(code, {sourceMap: {
            filename: "thirdparty.js",
            // url: "thirdparty.js.map"
          }, compress: {drop_console: true}});
          return {
            "thirdparty.js":min.code,
            // "thirdparty.js.map": min.map
          }
        },
      }, {
        // thirdparty.css
        src: [
          "../src/senaite/core/browser/static/thirdparty/jqueryui/themes/base/jquery-ui.min.css",
          "../src/senaite/core/browser/static/thirdparty/jqueryui/themes/base/theme.css",
          "../src/senaite/core/browser/static/thirdparty/combogrid/jquery.ui.combogrid-1.6.4.css",
        ],
        dest: code => ({
          "thirdparty.css":new CleanCSS({}).minify(code).styles,
        })
      }
    ]
    }, filesMap => {
      console.log("generated files: ",filesMap)
    }),
    // https://webpack.js.org/plugins/mini-css-extract-plugin/
    new MiniCssExtractPlugin({
      // N.B. use stable CSS name, because it is used in tinyMCE content as well
      //      -> see: `senaite.core.js`
      // filename: devMode ? "[name].css" : `[name]-${gitHash}.css`,
      filename: "[name].css"
    }),
    // https://webpack.js.org/plugins/copy-webpack-plugin/
    new CopyPlugin({
      patterns: [
        { from: "../node_modules/jquery/dist", to: path.resolve(staticPath, "modules/jquery") },
        { from: "../node_modules/jquery-form/dist", to: path.resolve(staticPath, "modules/jquery-form") },
        { from: "../node_modules/jquery-migrate/dist", to: path.resolve(staticPath, "modules/jquery-migrate") },
        { from: "../node_modules/bootstrap/dist", to: path.resolve(staticPath, "modules/bootstrap") },
        { from: "../node_modules/popper.js/dist/umd", to: path.resolve(staticPath, "modules/popperjs") },
        { from: "../node_modules/bootstrap-confirmation2/dist", to: path.resolve(staticPath, "modules/bootstrap-confirmation2") },
        { from: "../node_modules/bootstrap-select/dist", to: path.resolve(staticPath, "modules/bootstrap-select") },
        { from: "../node_modules/react/umd/react.production.min.js", to: path.resolve(staticPath, "modules/react") },
        { from: "../node_modules/react-dom/umd/react-dom.production.min.js", to: path.resolve(staticPath, "modules/react-dom") },
        { from: "../node_modules/tinymce", to: path.resolve(staticPath, "modules/tinymce"), globOptions: {ignore: ["**/README.md"],},},
        { from: "../node_modules/intl-tel-input/build", to: path.resolve(staticPath, "modules/intl-tel-input") },
        // { from: "../node_modules/@fortawesome/fontawesome-free", to: path.resolve(staticPath, "modules/fontawesome-free") },
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
