/** *** utilities **** */
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

///** *** movie category: ignored, to watch, watched **** */
//$(function() {
//	$('#content').on('click', function(e) {
//		var $btn = $(this);
//		if (!$btn.hasClass('disabled')) {
//			if (!$btn.hasClass('active')) {
//				var movie_id = $btn.attr('data-id');
//				$btn.addClass('disabled');
//				$.ajax({
//					type : 'POST',
//					url : '/api/movie/towatch',
//					data : {
//						id : movie_id
//					}
//				}).done(function() {
//					$btn.attr('title', '取消想看');
//					$btn.addClass('active');
//				}).fail(function(jqXHR) {
//					if (jqXHR.status == 401) { // unauthorized
//						$.cookie.raw = true;
//						$.cookie('next', window.location.href);
//						window.location.href = '/login';
//					}
//				}).always(function() {
//					$btn.removeClass('disabled');
//				});
//			} else {
//				var movie_id = $btn.attr('data-id');
//				$btn.addClass('disabled');
//				$.ajax({
//					type : 'delete',
//					url : '/api/movie/towatch/' + movie_id
//				}).done(function() {
//					$btn.attr('title', '想看本片');
//					$btn.removeClass('active');
//				}).fail(function(jqXHR) {
//					if (jqXHR.status == 401) { // unauthorized
//						$.cookie.raw = true;
//						$.cookie('next', window.location.href);
//						window.location.href = '/login';
//					}
//				}).always(function() {
//					$btn.removeClass('disabled');
//				});
//			}
//		}
//	}).on('click', '#watched', function(e) {
//		var $btn = $(this);
//		if (!$btn.hasClass('disabled')) {
//			if (!$btn.hasClass('active')) {
//				var movie_id = $btn.attr('data-id');
//				$btn.addClass('disabled');
//				$.ajax({
//					type : 'post',
//					url : '/api/movie/watched',
//					data : {
//						id : movie_id
//					}
//				}).done(function() {
//					$btn.attr('title', '取消看过');
//					$btn.addClass('active');
//					// deal with toWatch button
//					var $toWatchBtn = $btn.prev();
//					$toWatchBtn.attr('title', '想看本片');
//					$toWatchBtn.removeClass('active');
//					$toWatchBtn.hide();
//					// $btn.closest('li').hide()
//				}).fail(function(jqXHR) {
//					if (jqXHR.status == 401) { // unauthorized
//						$.cookie.raw = true;
//						$.cookie('next', window.location.href);
//						window.location.href = '/login';
//					}
//				}).always(function() {
//					$btn.removeClass('disabled');
//				});
//			} else {
//				var movie_id = $btn.attr('data-id');
//				$btn.addClass('disabled');
//				$.ajax({
//					type : 'delete',
//					url : '/api/movie/watched/' + movie_id
//				}).done(function() {
//					$btn.attr('title', '看过本片');
//					$btn.removeClass('active');
//					// deal with toWatch button
//					var $toWatchBtn = $btn.prev();
//					$toWatchBtn.attr('title', '想看本片');
//					$toWatchBtn.removeClass('active');
//					$toWatchBtn.show();
//				}).fail(function(jqXHR) {
//					if (jqXHR.status == 401) { // unauthorized
//						$.cookie.raw = true;
//						$.cookie('next', window.location.href);
//						window.location.href = '/login';
//					}
//				}).always(function() {
//					$btn.removeClass('disabled');
//				});
//			}
//		}
//	}).on('click', '#ignored', function(e) {
//		var $btn = $(this);
//		if (!$btn.hasClass('disabled')) {
//			var movie_id = $btn.attr('data-id');
//			$btn.addClass('disabled');
//			$.ajax({
//				type : 'post',
//				url : '/api/movie/ignored',
//				data : {
//					id : movie_id
//				}
//			}).done(function() {
//				$btn.attr('id', 'unwatched');
//				$btn.attr('title', '取消忽略');
//				$btn.addClass('active');
//				$btn.closest('li').hide()
//			}).fail(function(jqXHR) {
//				if (jqXHR.status == 401) { // unauthorized
//					$.cookie.raw = true;
//					$.cookie('next', window.location.href);
//					window.location.href = '/login';
//				}
//			}).always(function() {
//				$btn.removeClass('disabled');
//			});
//			;
//		}
//	}).on('click', '#unignored', function(e) {
//		var $btn = $(this);
//		if (!$btn.hasClass('disabled')) {
//			var movie_id = $btn.attr('data-id');
//			$btn.addClass('disabled');
//			$.ajax({
//				type : 'delete',
//				url : '/api/movie/ignored/' + movie_id
//			}).done(function() {
//				$btn.attr('id', 'ignored');
//				$btn.attr('title', '忽略本片');
//				$btn.removeClass('active');
//			}).fail(function(jqXHR) {
//				if (jqXHR.status == 401) { // unauthorized
//					$.cookie.raw = true;
//					$.cookie('next', window.location.href);
//					window.location.href = '/login';
//				}
//			}).always(function() {
//				$btn.removeClass('disabled');
//			});
//		}
//	});
//});