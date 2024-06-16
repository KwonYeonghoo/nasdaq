

document.addEventListener('DOMContentLoaded', (event) => {
    checkIsInWatchlist(watchlist_userId, watchlist_ticker);
  });


function checkIsInWatchlist(userId, ticker) {
    axios.get(`/api/v1/nasdaq/getOneWatchlist`, {
        params: {
            userId: userId,
            ticker: ticker,
        }
      })
      .then(response => {
        if (response.data) {
            isinWatchlist = true;
        } else {
            isinWatchlist = false;
        }
        updateWatchlistButton();
      })
      .catch(error => {
        console.error('Error checking watchlist status:', error);
      });
}

function updateWatchlistButton() {
    const watchlistButton = document.getElementById('watchlistButton');
    if (isinWatchlist) {
        watchlistButton.innerText = '관심종목 삭제';
        watchlistButton.classList.remove('btn-primary');
        watchlistButton.classList.add('btn-delete');
    } else {
        watchlistButton.innerText = '관심종목 추가';
          watchlistButton.classList.remove('btn-delete');
          watchlistButton.classList.add('btn-primary');
    }
}

function toggleWatchlist(userId, ticker, name) {
    const encodedUserId = encodeURIComponent(userId);
    const encodedTicker = encodeURIComponent(ticker);
    // const encodedName = encodeURIComponent(name);

    axios.post(`/api/v1/nasdaq/addWatchlist`, null, {
      params: {
          userId: encodedUserId,
          ticker: encodedTicker,
          name: name
      }
    })
    .then(response => {
      if (response.data === 1) {
          isinWatchlist = true;
          alert("관심종목에 추가되었습니다.")
      } else if (response.data === 0) {
          isinWatchlist = false;
          alert("관심종목에서 삭제되었습니다.")
      }
      updateWatchlistButton();
  })
    .catch(error => {
      alert('관심종목에 추가할 때 오류가 발생했습니다!');
      console.error('Error adding to watchlist:', error);
    });
  }