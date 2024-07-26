module.exports = [
  config => {
    config.optimization.splitChunks = {
      cacheGroups: {
        default: false,
      },
    };
    config.optimization.runtimeChunk = false;
    return config;
  },
  ['use-babel-config', '.babelrc'],
];
