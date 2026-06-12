import { CONFIG } from "@/const";
import { logger } from "@/utils/logger";
import axios, { AxiosRequestConfig } from "axios";

/** Resolve the API base URL from the current browser location. */
function baseUrl(): string {
    const { protocol, hostname, port } = globalThis.location;
    CONFIG.apiURL = `${protocol}//${hostname}${port ? ':' + port : ''}/api/v1/`;
    return CONFIG.apiURL;
}

function unwrap<T>(status: number, data: T): T {
    if ([200, 201].includes(status)) {
        return data;
    }
    throw new Error("Api Error " + JSON.stringify(data));
}

export async function get<T>(url: string, axiosOption: AxiosRequestConfig): Promise<T> {
    try {
        const response = await axios.get<T>(baseUrl() + url, axiosOption);
        return unwrap(response.status, response.data);
    } catch (error) {
        logger.error(error);
        return null as unknown as T;
    }
}

export async function post<T>(url: string, data: object, axiosOption: AxiosRequestConfig): Promise<T> {
    try {
        const response = await axios.post<T>(baseUrl() + url, data, axiosOption);
        return unwrap(response.status, response.data);
    } catch (error) {
        logger.error(error);
        return null as unknown as T;
    }
}

export async function put<T>(url: string, data: object, axiosOption: AxiosRequestConfig): Promise<T> {
    try {
        const response = await axios.put<T>(baseUrl() + url, data, axiosOption);
        return unwrap(response.status, response.data);
    } catch (error) {
        logger.error(error);
        return null as unknown as T;
    }
}

const api = {
    get,
    post,
    put
}

export default api;
