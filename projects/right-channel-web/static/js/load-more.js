$(function() {
	var scroll = 10;
	var isLoading = false;
	var hasMore = true;
	var nextPage = 1;

	function loadMore() {
		isLoading = true;
		qs = {
			genre : $('#genre').attr('data-genre'),
			country : $('#country').attr('data-country'),
			year : $('#year').attr('data-year'),
			sort : $('#sort').attr('data-sort'),
			resource : $('#resource').attr('data-resource'),
			page : nextPage
		};
		$.getJSON('/api/movie', qs, function(data) {
			if (data.movies.length > 0) {
				fillPosterTextView(data.movies);
			}
			hasMore = data.has_more;
			if (hasMore) {
				nextPage = nextPage + 1;
			} else if (data.movies.length === 0 && nextPage === 1) {
				$('#content').empty();
				$('#content').css('text-align', 'center');
				$('#content').append('没有找到符合条件的影片');
			}
		}).complete(function() {
			isLoading = false; // rest the status anyway
		});
	}

	function fillPosterTextView(movies) {
		var currLength = $('#content ul.galery').children().length;
		var elementsInRow = 3;
		var html = '';
		for ( var i = 0; i < movies.length; i++) {
			var li = '';
			if ((i + currLength) % elementsInRow == elementsInRow - 2) {
				if ((i + currLength) < elementsInRow)
					li = '<li class="first-row penultimate-child">';
				else
					li = '<li class="penultimate-child">';
			} else if ((i + currLength) % elementsInRow == elementsInRow - 1) {
				if ((i + currLength) < elementsInRow)
					li = '<li class="first-row last-child">';
				else
					li = '<li class="last-child">';
			} else {
				if ((i + currLength) < elementsInRow)
					li = '<li class="first-row">';
				else
					li = '<li>';
			}

			var poster_div = '<div class="pull-left poster-medium"><a href="/movie/'
					+ movies[i]._id
					+ '" target="_blank"><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQQAAAC0CAYAAABytVLLAAAIhElEQVR4Xu3avYsUWxMH4N7AL9DARM1EDNVQBP99IxMxUoxFMJBFENHAj/ftgbO07cxsrXW99K16TMT1TM2pp7p/0907J6enpz8nfwgQIPB/gROB4DggQGAICATHAgECZwICwcFAgIBAcAwQIPC7gCsERwUBAq4QHAMECLhCcAwQIHBEwC2Dw4MAAbcMjgECBNwyOAYIEHDL4BggQCAi4BlCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgbHDQr1+/nt69e3e2sxs3bkxPnjz5Zaenp6fTy5cvpx8/fux+vm/N27dvpzdv3py97t69e9P9+/f/uOMXL15M8/vevn17evTo0S91xv+NH+5b80/v548b8cKDAgJhYwfH+sQa21ue8Osw2HcSrk++seZPQ2FZb32yrwPs39jPxsZWZjsCYUOj/Pbt2/Ts2bPp+/fv0zhxlyfiw4cPp1u3bk3Pnz+fPn/+/Nuak5OT6enTp9OVK1fO1oyTd5y0V69e3V1tXLp0Kdz5sU//5Z7X7/W39hPeuIUXFhAIFyb7ey8YJ/84ka5duzatQ+Lu3bu70JhvFeaTf16z/rO8gphD5M6dO7tL/fkW4+fPn7vXffny5eyWY4TP+nXL8JnfYw6Tr1+//nLLsNxf5L0OrdnXx9+TVvmQgEDY+LGxPkkvX768O5Hnv+cT9OPHj7sOlpfx65N/HSzjpByf/HOdx48fT/O/5yuPUWsOnflq5Pr169ODBw9+u+qY33esWb5ufTXy6dOnX8Lo0H42PooW2xMIGx7z8mQbzxAOPRuY21ivOXalMT9cXH66z1cR79+/n5avWdLsO/HH/y/rjJ8t60SufDIPOzc8wv/c1gTCRke2PAH3nVzzttfPGca6Dx8+7H67cF4gzDWiT/6PBcJ5DzAFwkYPsj3bEggbnNWhMJi3GrkdGLcV43nBsUv05af7oauDQ7cG88+PPQgd9cbzish+NjiOVlsSCBsb97EwuGggzLXOe4i3/pXhvu8PHAuEyKf/zZs3zx5gnrefjY2j3XYEwsZGPh70XeRefn1SRn/tuLzamB8avnr1aveQcJy0kWcIy4eekV+V/hO/Bt3YyEptRyBsaJyHvnA0trjvhFtuf/npft59feS3A8vvKhx6hrD8+Zpy+WWq8/azoTG03opA2ND4D33jbx0Iy1uH8dXli35VeLzXoQeP63rHHirO+1l/eenf+Cr1hkZXZisCocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgL/A/1uMQYymAtG0AAAAASUVORK5CYII="></a></div>';
			var title_p = '<p><a href="/movie/' + movies[i]._id
					+ '" target="_blank" class="title">' + movies[i].title
					+ '</a> <span class="year">('
					+ ('year' in movies[i] ? movies[i].year : '未知')
					+ ')</span></p>';
			var rating_p = '<p><strong>评分:</strong> '
					+ ('douban' in movies[i] && 'rating' in movies[i].douban ? '<span class="rating" title="豆瓣评分'
							+ movies[i].douban.rating
							+ '">'
							+ movies[i].douban.rating + '</span>'
							: '未知') + '</p>';
			var genre_p = '<p><strong>类型:</strong> '
					+ ('genres' in movies[i] && movies[i].genres.length > 0 ? movies[i].genres
							.join(' / ')
							: '未知') + '</p>';
			var cast_p = '<p><strong>主演:</strong> '
					+ ('casts' in movies[i] && movies[i].casts.length > 0 ? movies[i].casts
							.join(' / ')
							: '未知') + '</p>';
			var desc_div = '<div class="pull-left desc"> ' + title_p + rating_p
					+ genre_p + cast_p + '</div>';

			var toolbar_div = '<div class="toolbar"><ul>'
					+ ('online' in movies[i] && movies[i].online.length > 0 ? '<li><a href="/movie/'
							+ movies[i]._id
							+ '" target="_blank" title="立即观看"><i class="icon-play"></i></a></li>'
							: '')
					+ ('download' in movies[i] && movies[i].download.length > 0 ? '<li><a href="/movie/'
							+ movies[i]._id
							+ '" target="_blank" title="立即下载"><i class="icon-download-alt"></i></a></li>'
							: '')
					+ '<li><a title="想看"><i class="icon-heart"></i></a></li><li><a title="看过"><i class="icon-check"></i></a></li></ul></div>';

			html += li + '<div class="galery-element">' + poster_div + desc_div
					+ toolbar_div + '</div>' + '</li>';
		}
		$('#content ul.galery').append(html);
	}

	$(window).scroll(
			function() {
				if ($(window).scrollTop() >= $(document).height()
						- $(window).height() - scroll) {
					if (!isLoading && hasMore)
						loadMore();
				}
			});

	loadMore();
});