import { get_jwt_token } from "./service.js";

export function downloadFile(fileId) {
    var token = get_jwt_token();
    var url = `/flrdownload/${fileId}?token=${token}`;
    window.location = url;
}

export function getSrcWithToken(fileId) {
    var token = get_jwt_token();
    return `/flrdownload/${fileId}?token=${token}`;
}