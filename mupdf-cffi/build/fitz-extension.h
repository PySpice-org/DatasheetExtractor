/**************************************************************************************************
 *
 * Add some helper functions and missing feature to MuPDF
 *
 *************************************************************************************************/

/**************************************************************************************************/

#ifndef __FITZ_EXTENSION_H__
#define __FITZ_EXTENSION_H__

/**************************************************************************************************/

#include <stdint.h>

#include "mupdf/fitz.h"

/***************************************************************************************************
 *
 * Provide FILE
 *
 */

// Fixme: inline ...
FILE * fz_fopen(const char * filename, const char * mode);

int fz_fclose(FILE * file);

/***************************************************************************************************
 *
 * Add missing copy functions
 *   Only fz_copy_matrix is available
 *
 */

static inline
fz_rect *
fz_copy_rect(fz_rect * restrict dst, const fz_rect * restrict src)
{
  *dst = *src;
  return dst;
}

static inline
fz_irect *
fz_copy_irect(fz_irect * restrict dst, const fz_irect * restrict src)
{
  *dst = *src;
  return dst;
}

/**************************************************************************************************/

int meta(fz_context * ctx, fz_document * doc, const char * key, char * string, char * buffer, int buffer_size);

/**************************************************************************************************/

// Missing feature
// Return the Metadata XML stream
// fz_buffer * pdf_metadata(fz_context *ctx, fz_document *doc);

/**************************************************************************************************/

void init(void);
fz_document * open_document(fz_context * ctx, const char *filename);
void python_throw_exit_callback(char * message);

/**************************************************************************************************/

#endif /* __FITZ_EXTENSION_H__ */
