export interface ApiResponse<Payload> {
    data?: Payload;
    errors: ApiError[];
    status: number;
}

export interface ApiError {
    kind: ErrorKind;
    message: string;
}

export enum ErrorKind {
    InvalidJson,
    JsonValidationError,
    UniqueViolationError,
    RecordNotFoundError,
    CookieNotSet,
    CookieNotFound,
    UserAlreadyPresent,
    WrongPassword,
    IncorrectParameters,
    NewsSourceNotFound,
    ServerError,
}
