const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

config.resolver.sourceExts = ['js', 'json', 'ts', 'tsx'];
config.resolver.unstable_allowRequireContext = true;
config.server = {
  middleware: [],
  rewriteRequestUrl: (url) => {
    return url;
  }
};

module.exports = config;
