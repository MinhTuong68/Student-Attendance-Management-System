const globalLoader = document.getElementById('globalLoader');
const loaderText = document.getElementById('loaderText');

function showLoader(message = "Đang xử lý..."){
    if(loaderText) loaderText.innerText = message;
    if(globalLoader){
        globalLoader.classList.remove('hidden');
        globalLoader.classList.add('flex');
    }
}

function hideLoader(){
    if (globalLoader){
        globalLoader.classList.add('hidden');
        globalLoader.classList.remove('flex');
    }
}