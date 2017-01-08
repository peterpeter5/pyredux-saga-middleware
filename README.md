# pyredux-saga-implementation

WIP (highly unstable and naively implemented)

Loosely inspired by [redux-saga-js](https://github.com/redux-saga/redux-saga)

future work and documentation have to been done. At the moment
only blocking calls with ```put``` and ```call``` are implemented.
```take_every``` just binds saga to ```Trampoline```. No Concurrency
is implemented at the moment!

For some examples checkout the test-cases