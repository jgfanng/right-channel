function userActionMark($btn) {
	if (!$btn.hasClass('disabled')) {
		var id = $btn.attr('data-id');
		var action = $btn.attr('data-action');
		$btn.addClass('disabled');
		$.ajax({
			type : 'post',
			url : '/api/movie/{0}'.format(action),
			data : {
				id : id
			}
		}).done(function() {
			$btn.removeClass('unmarked');
			$btn.addClass('marked');
			$btn.children('i').addClass('icon-white');
			if (action == 'towatch') {
				$btn.addClass('btn-info');
				$btn.attr('title', '已加入想看列表');
			} else if (action == 'watched') {
				$btn.addClass('btn-success');
				$btn.attr('title', '已加入已看列表');
			} else if (action == 'notinterested') {
				$btn.addClass('btn-inverse');
				$btn.attr('title', '已标记为没兴趣');
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

function userActionUnmark($btn) {
	if (!$btn.hasClass('disabled')) {
		var id = $btn.attr('data-id');
		var action = $btn.attr('data-action');
		$btn.addClass('disabled');
		$.ajax({
			type : 'delete',
			url : '/api/movie/{0}/{1}'.format(action, id)
		}).done(function() {
			$btn.removeClass('marked');
			$btn.addClass('unmarked');
			$btn.children('i').removeClass('icon-white');
			if (action == 'towatch') {
				$btn.removeClass('btn-info');
				$btn.attr('title', '加入想看列表');
			} else if (action == 'watched') {
				$btn.removeClass('btn-success');
				$btn.attr('title', '加入已看列表');
			} else if (action == 'notinterested') {
				$btn.removeClass('btn-inverse');
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