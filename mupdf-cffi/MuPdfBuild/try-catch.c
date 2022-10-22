fz_try(ctx)
{
  // Try to perform a task. Never 'return', 'goto' or 'longjmp' out of
  // here. 'break' may be used to safely exit (just) the try block
  // scope.
}
fz_catch(ctx)
{
  // This code is called (after any always block) only if something
  // within the fz_try block (including any functions it called) threw
  // an exception. The code here is expected to handle the exception
  // (maybe record/report the error, cleanup any stray state etc) and
  // can then either exit the block, or pass on the exception to a
  // higher level (enclosing) fz_try block (using fz_throw, or
  // fz_rethrow).
}

if (fz_push_try(ctx->error) &&
    ((ctx->error->stack[ctx->error->top].code = fz_setjmp(ctx->error->stack[ctx->error->top].buffer)) == 0))
  {
    do
      {
	{
	  // ...
	}
      } while(0);
  }
if (ctx->error->stack[ctx->error->top--].code > 1)
  {
    // ..
  }
