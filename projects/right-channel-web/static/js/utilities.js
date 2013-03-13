$(function() {
	String.prototype.format = function() {
		var s = this;
		for ( var i = 0; i < arguments.length; i++) {
			var reg = new RegExp('\\{' + i + '\\}', 'gm');
			s = s.replace(reg, arguments[i]);
		}

		return s;
	};
});