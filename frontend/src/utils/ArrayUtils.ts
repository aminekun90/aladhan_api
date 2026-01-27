export { };

declare global {
  interface Array<T> {
    count(predicat: (item: T) => boolean): number;
  }
}

if (!Array.prototype.count) {
  Array.prototype.count = function<T>(this: T[], predicat: (item: T) => boolean): number {
    return this.reduce((acc, item) => (predicat(item) ? acc + 1 : acc), 0);
  };
}

