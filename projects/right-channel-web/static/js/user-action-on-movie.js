function performUserActionOnMovie($btn) {
	if (!$btn.hasClass('disabled')) {
		var id = $btn.attr('data-id');
		var action = $btn.attr('data-action');
		var nextOperation = $btn.attr('data-next-operation');
		$btn.addClass('disabled');
		$.ajax(
			(nextOperation == 'mark') ? {
				type : 'post',
				url : '/api/movie/{0}'.format(type),
				data : {
					id : id
				}
			} : {
				type : 'delete',
				url : '/api/movie/{0}/{1}'.formar(type, id)
			}
		).done(function() {
			if (action == 'toWatch') {
				if (nextOperation == 'mark') {
					$btn.addClass('btn-primary');
					$btn.children('i').addClass('icon-white');
					$btn.attr('title', '从想看列表中移除');
				} else {
					$btn.removeClass('btn-primary');
					$btn.children('i').removeClass('icon-white');
					$btn.attr('title', '加入想看列表');
				}
			} else if (action == 'watched') {
				if (nextOperation == 'mark') {
					$btn.addClass('btn-success');
					$btn.children('i').addClass('icon-white');
					$btn.attr('title', '从已看列表中移除');
				} else {
					$btn.removeClass('btn-success');
					$btn.children('i').removeClass('icon-white');
					$btn.attr('title', '加入已看列表');
				}
			} else if (action == 'notInterested') {
				if (nextOperation == 'mark') {
					$btn.addClass('btn-inverse');
					$btn.children('i').addClass('icon-white');
					$btn.attr('title', '取消标记');
				} else {
					$btn.removeClass('btn-inverse');
					$btn.children('i').removeClass('icon-white');
					$btn.attr('title', '标记为没兴趣');
				}
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