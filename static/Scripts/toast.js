var toasts = [].slice.call(document.querySelectorAll('.toast'))
var toastList = toasts.map(function (toast) {
    return new bootstrap.Toast(toast)
})
toastList.forEach(toast => toast.show())