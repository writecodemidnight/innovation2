// URL 模块 polyfill for 微信小程序
// 提供基础的 URL 解析功能

function Url() {
  this.protocol = null;
  this.slashes = null;
  this.auth = null;
  this.host = null;
  this.port = null;
  this.hostname = null;
  this.hash = null;
  this.search = null;
  this.query = null;
  this.pathname = null;
  this.path = null;
  this.href = null;
}

function urlParse(url, parseQueryString) {
  if (!url) {
    return new Url();
  }

  var parsed = new Url();
  parsed.href = url;

  // Simple URL parsing for mini-program environment
  var match = url.match(/^(https?:)\/\/([^\/]+)(\/[^?]*)?(\?.*)?(#.*)?$/);
  if (match) {
    parsed.protocol = match[1];
    parsed.slashes = true;
    var hostParts = match[2].split(':');
    parsed.hostname = hostParts[0];
    parsed.port = hostParts[1] || null;
    parsed.host = match[2];
    parsed.pathname = match[3] || '/';
    parsed.search = match[4] || null;
    parsed.hash = match[5] || null;
    parsed.path = (parsed.pathname || '') + (parsed.search || '');

    if (parseQueryString && parsed.search) {
      parsed.query = {};
      var queryString = parsed.search.substring(1);
      var pairs = queryString.split('&');
      for (var i = 0; i < pairs.length; i++) {
        var pair = pairs[i].split('=');
        if (pair[0]) {
          parsed.query[decodeURIComponent(pair[0])] = decodeURIComponent(pair[1] || '');
        }
      }
    }
  }

  return parsed;
}

function urlFormat(obj) {
  if (typeof obj === 'string') {
    return obj;
  }

  var protocol = obj.protocol || '';
  var host = obj.host || '';
  var pathname = obj.pathname || '';
  var search = obj.search || '';
  var hash = obj.hash || '';

  if (!search && obj.query) {
    var queryStr = '';
    for (var key in obj.query) {
      if (obj.query.hasOwnProperty(key)) {
        queryStr += (queryStr ? '&' : '') + encodeURIComponent(key) + '=' + encodeURIComponent(obj.query[key]);
      }
    }
    search = queryStr ? '?' + queryStr : '';
  }

  return protocol + (protocol ? '//' : '') + host + pathname + search + hash;
}

function resolve(from, to) {
  if (!to) return from;
  if (to.indexOf('://') !== -1) return to;

  var fromParsed = urlParse(from);
  var resolvedPath;

  if (to.charAt(0) === '/') {
    resolvedPath = to;
  } else {
    var fromPath = fromParsed.pathname || '/';
    var fromDir = fromPath.substring(0, fromPath.lastIndexOf('/') + 1);
    resolvedPath = fromDir + to;
  }

  // Normalize path
  var parts = resolvedPath.split('/');
  var result = [];
  for (var i = 0; i < parts.length; i++) {
    if (parts[i] === '..') {
      result.pop();
    } else if (parts[i] !== '.' && parts[i] !== '') {
      result.push(parts[i]);
    }
  }

  resolvedPath = '/' + result.join('/');

  return urlFormat({
    protocol: fromParsed.protocol,
    host: fromParsed.host,
    pathname: resolvedPath,
    search: to.indexOf('?') !== -1 ? to.substring(to.indexOf('?')) : null
  });
}

module.exports = {
  parse: urlParse,
  format: urlFormat,
  resolve: resolve,
  Url: Url
};
