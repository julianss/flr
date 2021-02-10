import { get_jwt_token } from "./service.js";

export function downloadFile(fileId) {
    var token = get_jwt_token();
    var url = `/flrdownload/${fileId}?token=${token}`;
    window.location = url;
}