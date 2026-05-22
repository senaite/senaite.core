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

const mode = process.env.mode;
const isDev = mode === "development";
const isProd = mode === "production";
const staticPath = path.resolve(__dirname, "../src/senaite/core/browser/static");

console.log(`RUNNING WEBPACK IN '${mode}' MODE`);


module.exports = {
  // https://webpack.js.org/configuration/devtool
  devtool: isDev ? "eval" : "source-map",
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
    filename: isDev ? "[name].js" : `[name].[contenthash].js`,
    path: path.resolve(staticPath, "bundles"),
    publicPath: "/++plone++senaite.core.static/bundles/"
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
            loader: "babel-loader",
            options: { cacheDirectory: true },
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
            loader: "css-loader",
            options: { sourceMap: isDev },
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
            loader: "css-loader",
            options: {
              sourceMap: isDev,
              // Skip URLs that point at Plone-served resources;
              // they should pass through verbatim and be resolved
              // by the browser at runtime.
              url: {
                filter: (url) => !url.startsWith("/"),
              },
            },
          },
          {
            // https://webpack.js.org/loaders/sass-loader/
            loader: "sass-loader",
            options: { sourceMap: isDev },
          }
        ]
      },
      {
        test: /\.(woff(2)?|ttf|eot|svg)(\?v=\d+\.\d+\.\d+)?$/,
        // https://webpack.js.org/guides/asset-modules
        type: "asset/resource",
        generator: {
          filename: "../fonts/[name][ext]",
          publicPath: "/++plone++senaite.core.static/fonts/"
        }
      },
      {
        test: /\.(png|jpg)(\?v=\d+\.\d+\.\d+)?$/,
        // https://webpack.js.org/guides/asset-modules
        type: "asset/resource",
        generator: {
          filename: "../assets/img/[name][ext]",
          publicPath: "/++plone++senaite.core.static/assets/img/"
        }
      }
    ]
  },
  optimization: {
    minimize: isProd,
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
          "../src/senaite/core/browser/static/js/senaite.core.analysisrequest.js",
          "../src/senaite/core/browser/static/js/senaite.core.bikasetup.js",
          "../src/senaite/core/browser/static/js/senaite.core.calculation.edit.js",
          "../src/senaite/core/browser/static/js/senaite.core.client.js",
          "../src/senaite/core/browser/static/js/senaite.core.common.js",
          "../src/senaite/core/browser/static/js/senaite.core.graphics.controlchart.js",
          "../src/senaite/core/browser/static/js/senaite.core.graphics.range.js",
          "../src/senaite/core/browser/static/js/senaite.core.instrument.js",
          "../src/senaite/core/browser/static/js/senaite.core.loader.js",
          "../src/senaite/core/browser/static/js/senaite.core.partitionmagic.js",
          "../src/senaite/core/browser/static/js/senaite.core.referencesample.js",
          "../src/senaite/core/browser/static/js/senaite.core.setupview.js",
          "../src/senaite/core/browser/static/js/senaite.core.site.js",
          "../src/senaite/core/browser/static/js/senaite.core.utils.attachments.js",
          "../src/senaite/core/browser/static/js/senaite.core.utils.barcode.js",
          "../src/senaite/core/browser/static/js/senaite.core.worksheet.js",
          "../src/senaite/core/browser/static/js/senaite.core.worksheet.print.js",
        ],
        dest: code => {
          const joined = Array.isArray(code) ? code.join("\n") : code;

          if (isDev) {
            return { "legacy.js": joined };
          }

          const min = uglifyJS.minify(joined, {
            compress: { drop_console: true },
            mangle: false,
            keep_fnames: true
          });

          if (min.error) {
            console.error("UglifyJS error:", min.error);
            throw min.error;
          }

          if (!min.code || typeof min.code !== "string") {
            throw new Error("UglifyJS output is empty or invalid for legacy.js");
          }

          return { "legacy.js": min.code };
        }
      }, {
        // thirdparty.js
        src: [
          "../src/senaite/core/browser/static/thirdparty/plone/jquery.tools.js",
          "../src/senaite/core/browser/static/thirdparty/plone/overlayhelpers.js",
          "../src/senaite/core/browser/static/thirdparty/jquery-barcode-2.2.0.min.js",
          "../src/senaite/core/browser/static/thirdparty/jquery-qrcode-0.17.0.min.js",
        ],
        dest: code => {
          // no minifying of already minified code
          const joined = Array.isArray(code) ? code.join("\n") : code;
          return { "thirdparty.js": joined };
        }
      }, {
        // legacy.css
        src: [
          "../src/senaite/core/browser/static/css/senaite.core.graphics.css",
          "../src/senaite/core/browser/static/thirdparty/plone/overlays.css",
        ],
        dest: code => ({
          "legacy.css":new CleanCSS({}).minify(code).styles,
        })
      }, {
        // thirdparty.css
        src: [],
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
      // filename: isDev ? "[name].css" : `[name]-${gitHash}.css`,
      filename: "[name].css"
    }),
    // https://webpack.js.org/plugins/copy-webpack-plugin/
    new CopyPlugin({
      patterns: [
        { from: "../node_modules/bootstrap-confirmation2/dist", to: path.resolve(staticPath, "modules/bootstrap-confirmation2") },
        { from: "../node_modules/bootstrap-select/dist", to: path.resolve(staticPath, "modules/bootstrap-select") },
        { from: "../node_modules/bootstrap/dist", to: path.resolve(staticPath, "modules/bootstrap") },
        { from: "../node_modules/d3/dist", to: path.resolve(staticPath, "modules/d3") },
        { from: "../node_modules/@fortawesome/fontawesome-free/webfonts", to: path.resolve(staticPath, "webfonts") },
        { from: "../node_modules/handlebars/dist", to: path.resolve(staticPath, "modules/handlebars") },
        { from: "../node_modules/intl-tel-input/build", to: path.resolve(staticPath, "modules/intl-tel-input") },
        { from: "../node_modules/jquery-form/dist", to: path.resolve(staticPath, "modules/jquery-form") },
        { from: "../node_modules/jquery-ui/dist", to: path.resolve(staticPath, "modules/jquery-ui") },
        { from: "../node_modules/jquery/dist", to: path.resolve(staticPath, "modules/jquery") },
        { from: "../node_modules/popper.js/dist/umd", to: path.resolve(staticPath, "modules/popperjs") },
        { from: "../node_modules/tinymce", to: path.resolve(staticPath, "modules/tinymce"), globOptions: {ignore: ["**/README.md"],},},
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
    $: "jQuery",
    jquery: "jQuery",
    bootstrap: "bootstrap",
    tinyMCE: "tinymce"
  }
};
