/**************************************************************************************************/

FILE * fz_fopen(const char *filename, const char *mode);
// fz_buffer * pdf_metadata(fz_context *ctx, fz_document *doc);
fz_irect * fz_copy_irect(fz_irect * dst, const fz_irect * src);
fz_rect * fz_copy_rect(fz_rect * dst, const fz_rect * src);
int fz_fclose(FILE *file);
int meta(fz_context *ctx, fz_document *doc, const char *key, char *string, char *buffer, int buffer_size);

void init();
void python_throw_exit_callback(char *message);
fz_document * open_document (fz_context * ctx, const char *filename);
