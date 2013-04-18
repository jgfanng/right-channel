function toggleToWatch($btn) {
	if (!$btn.hasClass('disabled')) {
		var id = $btn.attr('data-id');
		var currStatus = $btn.attr('data-current-status');
		$btn.addClass('disabled');
		$.ajax(
			(currStatus == 'unmarked') ? {
				type : 'post',
				url : '/api/movie/towatch',
				data : {
					id : id
				}
			} : {
				type : 'delete',
				url : '/api/movie/towatch/{0}'.format(id)
			}
		).done(function() {
			if (currStatus == 'unmarked') {
				$btn.addClass('btn-info');
				$btn.children('i').addClass('icon-white');
				$btn.attr('data-current-status', 'marked');
				$btn.attr('title', '已加入想看列表');
			} else {
				$btn.removeClass('btn-info');
				$btn.children('i').removeClass('icon-white');
				$btn.attr('data-current-status', 'unmarked');
				$btn.attr('title', '加入想看列表');
			}
		}).fail(function(jqXHR) {
			if (jqXHR.status == 401) { // unauthorized
				$.cookie.raw = true;
				$.cookie('next', window.location.href);
				window.location.href = '/login';
			}
		}).always(function() {
			$btn.removeClass('disabled');
		});
	}
}

function toggleWatched($btn) {
	if (!$btn.hasClass('disabled')) {
		var id = $btn.attr('data-id');
		var currStatus = $btn.attr('data-current-status');
		$btn.addClass('disabled');
		$.ajax(
			(currStatus == 'unmarked') ? {
				type : 'post',
				url : '/api/movie/watched',
				data : {
					id : id
				}
			} : {
				type : 'delete',
				url : '/api/movie/watched/{0}'.format(id)
			}
		).done(function() {
			if (currStatus == 'unmarked') {
				$btn.addClass('btn-success');
				$btn.children('i').addClass('icon-white');
				$btn.attr('data-current-status', 'marked');
				$btn.attr('title', '已加入已看列表');
			} else {
				$btn.removeClass('btn-success');
				$btn.children('i').removeClass('icon-white');
				$btn.attr('data-current-status', 'unmarked');
				$btn.attr('title', '加入已看列表');
			}
		}).fail(function(jqXHR) {
			if (jqXHR.status == 401) { // unauthorized
				$.cookie.raw = true;
				$.cookie('next', window.location.href);
				window.location.href = '/login';
			}
		}).always(function() {
			$btn.removeClass('disabled');
		});
	}
}

function toggleNotInterested($btn) {
	if (!$btn.hasClass('disabled')) {
		var id = $btn.attr('data-id');
		var currStatus = $btn.attr('data-current-status');
		$btn.addClass('disabled');
		$.ajax(
			(currStatus == 'unmarked') ? {
				type : 'post',
				url : '/api/movie/notinterested',
				data : {
					id : id
				}
			} : {
				type : 'delete',
				url : '/api/movie/notinterested/{0}'.format(id)
			}
		).done(function() {
			if (currStatus == 'unmarked') {
				$btn.addClass('btn-inverse');
				$btn.children('i').addClass('icon-white');
				$btn.attr('data-current-status', 'marked');
				$btn.attr('title', '已标记为没兴趣');
			} else {
				$btn.removeClass('btn-inverse');
				$btn.children('i').removeClass('icon-white');
				$btn.attr('data-current-status', 'unmarked');
				$btn.attr('title', '标记为没兴趣');
			}
		}).fail(function(jqXHR) {
			if (jqXHR.status == 401) { // unauthorized
				$.cookie.raw = true;
				$.cookie('next', window.location.href);
				window.location.href = '/login';
			}
		}).always(function() {
			$btn.removeClass('disabled');
		});
	}
}