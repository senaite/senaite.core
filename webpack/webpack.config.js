const path = require("path");
const webpack = require("webpack");
const childProcess = require("child_process");

const CleanCSS = require("clean-css");
const CopyPlugin = require("copy-webpack-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const MergeIntoSingleFilePlugin = require("webpack-merge-and-include-globally");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const TerserPlugin = require('terser-webpack-plugin');
const uglifyJS = require("uglify-js");
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
  optimization: {
    minimize: true,
    minimizer: [
      // https://v4.webpack.js.org/plugins/terser-webpack-plugin/
      new TerserPlugin({
        extractComments: true,
        sourceMap: true, // Must be set to true if using source-maps in production
        exclude: /\/modules/,
        terserOptions: {
          // https://github.com/webpack-contrib/terser-webpack-plugin#terseroptions
          extractComments: true,
          compress: {
            drop_console: true,
          },
	      }
      }),
      // https://webpack.js.org/plugins/css-minimizer-webpack-plugin/
      new CssMinimizerPlugin({
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
    // https://github.com/markshapiro/webpack-merge-and-include-globally
    new MergeIntoSingleFilePlugin({
      files: [{
        src: [
          // legacy.js
          "../src/senaite/core/browser/static/js/bika.lims.analysisprofile.js",
          "../src/senaite/core/browser/static/js/bika.lims.analysisrequest.js",
          "../src/senaite/core/browser/static/js/bika.lims.analysisservice.js",
          "../src/senaite/core/browser/static/js/bika.lims.artemplate.js",
          "../src/senaite/core/browser/static/js/bika.lims.batch.js",
          "../src/senaite/core/browser/static/js/bika.lims.bikasetup.js",
          "../src/senaite/core/browser/static/js/bika.lims.calculation.edit.js",
          "../src/senaite/core/browser/static/js/bika.lims.client.js",
          "../src/senaite/core/browser/static/js/bika.lims.common.js",
          "../src/senaite/core/browser/static/js/bika.lims.department.js",
          "../src/senaite/core/browser/static/js/bika.lims.graphics.controlchart.js",
          "../src/senaite/core/browser/static/js/bika.lims.graphics.range.js",
          "../src/senaite/core/browser/static/js/bika.lims.instrument.import.js",
          "../src/senaite/core/browser/static/js/bika.lims.instrument.js",
          "../src/senaite/core/browser/static/js/bika.lims.method.js",
          "../src/senaite/core/browser/static/js/bika.lims.referencesample.js",
          "../src/senaite/core/browser/static/js/bika.lims.reflexrule.js",
          "../src/senaite/core/browser/static/js/bika.lims.rejection.js",
          "../src/senaite/core/browser/static/js/bika.lims.reports.js",
          "../src/senaite/core/browser/static/js/bika.lims.site.js",
          "../src/senaite/core/browser/static/js/bika.lims.utils.attachments.js",
          "../src/senaite/core/browser/static/js/bika.lims.utils.barcode.js",
          "../src/senaite/core/browser/static/js/bika.lims.worksheet.js",
          "../src/senaite/core/browser/static/js/bika.lims.worksheet.print.js",
          "../src/senaite/core/browser/static/js/bika.lims.worksheettemplate.js",
          "../src/senaite/core/browser/static/js/bika.lims.loader.js",
        ],
        dest: code => {
          const min = uglifyJS.minify(code, {sourceMap: {
            filename: "legacy.js",
            url: "legacy.js.map"
          }, compress: {drop_console: true}});
          return {
            "legacy.js":min.code,
            "legacy.js.map": min.map
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
          "../src/senaite/core/browser/static/thirdparty/timepicker/jquery-ui-timepicker-addon-1.6.3.min.js",
          "../src/senaite/core/browser/static/thirdparty/timepicker/i18n/jquery-ui-timepicker-addon-i18n-1.6.3.min.js",
          "../src/senaite/core/browser/static/thirdparty/combogrid/jquery.ui.combogrid-1.6.4.js",
          "../src/senaite/core/browser/static/thirdparty/plone/overlayhelpers.js",
          "../src/senaite/core/browser/static/thirdparty/jquery-barcode-2.2.0.min.js",
          "../src/senaite/core/browser/static/thirdparty/jquery-qrcode-0.17.0.min.js",
          "../src/senaite/core/browser/static/thirdparty/d3.js",
        ],
        dest: code => {
          const min = uglifyJS.minify(code, {sourceMap: {
            filename: "thirdparty.js",
            url: "thirdparty.js.map"
          }, compress: {drop_console: true}});
          return {
            "thirdparty.js":min.code,
            "thirdparty.js.map": min.map
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
        { from: "../node_modules/jquery/dist", to: path.resolve(staticPath, "modules/jquery") },
        { from: "../node_modules/jquery-form/dist", to: path.resolve(staticPath, "modules/jquery-form") },
        { from: "../node_modules/jquery-migrate/dist", to: path.resolve(staticPath, "modules/jquery-migrate") },
        { from: "../node_modules/bootstrap/dist", to: path.resolve(staticPath, "modules/bootstrap") },
        { from: "../node_modules/popper.js/dist/umd", to: path.resolve(staticPath, "modules/popperjs") },
        { from: "../node_modules/bootstrap-confirmation2/dist", to: path.resolve(staticPath, "modules/bootstrap-confirmation2") },
        { from: "../node_modules/react/umd", to: path.resolve(staticPath, "modules/react") },
        { from: "../node_modules/react-dom/umd", to: path.resolve(staticPath, "modules/react-dom") },
        { from: "../node_modules/tinymce", to: path.resolve(staticPath, "modules/tinymce") },
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
