$(function() {
	function loadFlash(provider, id) {
		if (provider == 'pptv') {
			swfobject.embedSWF('http://player.pptv.com/v/{0}.swf'.format(id),
					'flashContent', '800', '500', '10.0.0', null, null, {
						quality: 'high',
						allowScriptAccess : 'always',
						allownetworking : 'all',
						allowfullscreen : 'true'
					});
		}
	}

	function loadFirstFlash() {
		var $provider = $('#online a:first');
		if ($provider) {
			if ($provider.attr('data-provider') == 'pptv')
				loadFlash($provider.attr('data-provider'), $provider
						.attr('data-id'));
		}
	}

	loadFirstFlash();
});