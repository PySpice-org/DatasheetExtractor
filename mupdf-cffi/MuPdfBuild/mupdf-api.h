/**************************************************************************************************
 *
 * Constants
 *
 */

enum {
  FZ_STORE_UNLIMITED = 0,
  // FZ_STORE_DEFAULT = 256 << 20,
};

enum
{
  // Hints
  FZ_DONT_INTERPOLATE_IMAGES = 1,
  FZ_MAINTAIN_CONTAINER_STACK = 2,
  FZ_NO_CACHE = 4,
};

// stext_options.flags
enum
{
  FZ_STEXT_PRESERVE_LIGATURES = 1,
  FZ_STEXT_PRESERVE_WHITESPACE = 2,
  FZ_STEXT_PRESERVE_IMAGES = 4
};

enum
{
  FZ_STEXT_BLOCK_TEXT = 0,
  FZ_STEXT_BLOCK_IMAGE = 1
};

/***************************************************************************************************
 *
 * Structures
 *
 */

typedef struct _IO_FILE FILE;

typedef struct fz_alloc_context_s fz_alloc_context;
typedef struct fz_buffer_s fz_buffer;
typedef struct fz_colorspace_s fz_colorspace;
typedef struct fz_context_s fz_context;
typedef struct fz_cookie_s fz_cookie;
typedef struct fz_device_s fz_device;
typedef struct fz_display_list_s fz_display_list;
typedef struct fz_document_s fz_document;
typedef struct fz_font_s fz_font;
typedef struct fz_image_block_s fz_image_block;
typedef struct fz_image_s fz_image;
typedef struct fz_irect_s fz_irect;
typedef struct fz_link_s fz_link;
typedef struct fz_locks_context_s fz_locks_context;
typedef struct fz_matrix_s fz_matrix;
typedef struct fz_output_s fz_output;
typedef struct fz_page_block_s fz_page_block;
typedef struct fz_page_s fz_page;
typedef struct fz_pixmap_s fz_pixmap;
typedef struct fz_point_s fz_point;
typedef struct fz_pool_s fz_pool;
typedef struct fz_rect_s fz_rect;
typedef struct fz_scale_cache_s fz_scale_cache;
typedef struct fz_separations_s fz_separations;
typedef struct fz_stext_block_s fz_stext_block;
typedef struct fz_stext_char_s fz_stext_char;
typedef struct fz_stext_line_s fz_stext_line;
typedef struct fz_stext_options_s fz_stext_options;
typedef struct fz_stext_page_s fz_stext_page;
typedef struct fz_stream_s fz_stream;

/***************************************************************************************************
 *
 * Structures Details
 *
 */

struct fz_matrix_s
{
  float a, b, c, d, e, f;
};

struct fz_point_s
{
  float x, y;
};

struct fz_irect_s
{
  int x0, y0;
  int x1, y1;
};

struct fz_rect_s
{
  float x0, y0;
  float x1, y1;
};

/**************************************************************************************************/

struct fz_stext_options_s
{
  int flags;
};

// A text page is a list of blocks, together with an overall bounding box.
struct fz_stext_page_s
{
  fz_pool * pool;
  fz_rect mediabox;
  fz_stext_block * first_block, * last_block;
};

// A text block is a list of lines of text (typically a paragraph), or an image.
struct fz_stext_block_s
{
  int type;
  fz_rect bbox;
  union {
    struct { fz_stext_line * first_line, * last_line; } t;
    struct { fz_matrix transform; fz_image * image; } i;
  } u;
  fz_stext_block * prev, * next;
};

// A text line is a list of characters that share a common baseline.
struct fz_stext_line_s
{
  int wmode; // 0 for horizontal, 1 for vertical
  fz_point dir; // normalized direction of baseline
  fz_rect bbox;
  fz_stext_char * first_char, * last_char;
  fz_stext_line * prev, * next;
};

// A text char is a unicode character, the style in which is appears, and
// the point at which it is positioned.
struct fz_stext_char_s
{
  int c;
  fz_point origin;
  fz_rect bbox;
  float size;
  fz_font * font;
  fz_stext_char * next;
};

/***************************************************************************************************
 *
 * Functions
 *
 */

// buffer
void fz_drop_buffer (fz_context * ctx, fz_buffer * buf);
size_t fz_buffer_storage(fz_context * ctx, fz_buffer * buf, unsigned char ** datap);
const char * fz_string_from_buffer(fz_context * ctx, fz_buffer * buf);

// colorspace
fz_colorspace * fz_device_rgb (fz_context * ctx);

// context
void fz_drop_context (fz_context * ctx);
const char *fz_caught_message(fz_context * ctx);
fz_context * fz_new_context (fz_alloc_context * alloc, fz_locks_context * locks, unsigned int max_store);
void fz_set_aa_level (fz_context * ctx, int bits);

// device
void fz_drop_device (fz_context * ctx, fz_device * dev);
void fz_close_device(fz_context * ctx, fz_device * dev);
void fz_enable_device_hints(fz_context * ctx, fz_device * dev, int hints);
fz_device * fz_new_draw_device(fz_context * ctx, const fz_matrix * transform, fz_pixmap * dest);

// display-list
void fz_drop_display_list(fz_context * ctx, fz_display_list * list);
fz_display_list * fz_new_display_list(fz_context * ctx, const fz_rect * mediabox);
fz_device * fz_new_list_device(fz_context * ctx, fz_display_list * list);
void fz_run_display_list(fz_context * ctx, fz_display_list * list, fz_device * dev, const fz_matrix * ctm, const fz_rect * area, fz_cookie * cookie);

// document
void fz_drop_document (fz_context * ctx, fz_document * doc);
void fz_drop_page (fz_context * ctx, fz_page * page);
fz_rect * fz_bound_page(fz_context * ctx, fz_page * page, fz_rect * rect);
int fz_count_pages (fz_context * ctx, fz_document * doc);
fz_link * fz_load_links(fz_context * ctx, fz_page * page);
int fz_lookup_metadata(fz_context * ctx, fz_document * doc, const char * key, char * buf, int size);
fz_document * fz_open_document (fz_context * ctx, const char *filename);
// fz_document * fz_open_document_with_stream (fz_context * ctx, const char * magic, fz_stream * stream);
void fz_register_document_handlers(fz_context * ctx);
void fz_run_page(fz_context * ctx, fz_page * page, fz_device * dev, const fz_matrix * transform, fz_cookie * cookie);
void fz_run_page_contents(fz_context * ctx, fz_page * page, fz_device * dev, const fz_matrix * transform, fz_cookie * cookie); // set cookie to null

// font
int fz_font_is_bold(fz_context * ctx, fz_font * font);
int fz_font_is_italic(fz_context * ctx, fz_font * font);
const char * fz_font_name(fz_context * ctx, fz_font * font);

// geometry
extern const fz_matrix fz_identity;
 extern const fz_rect fz_infinite_rect;
fz_matrix * fz_concat (fz_matrix * result, const fz_matrix * left, const fz_matrix * right);
fz_matrix * fz_pre_rotate (fz_matrix * m, float degrees);
fz_matrix * fz_pre_scale (fz_matrix * m, float sx, float sy);
fz_rect * fz_rect_from_irect(fz_rect * restrict rect, const fz_irect * restrict bbox);
fz_irect * fz_round_rect(fz_irect * restrict bbox, const fz_rect * restrict rect);
fz_matrix * fz_rotate (fz_matrix * m, float degrees);
fz_matrix * fz_scale (fz_matrix * m, float sx, float sy);
fz_rect * fz_transform_rect(fz_rect * restrict rect, const fz_matrix * restrict transform);

// pixmap
void fz_drop_pixmap (fz_context * ctx, fz_pixmap * pix);
void fz_clear_pixmap_with_value(fz_context * ctx, fz_pixmap * pix, int value);
fz_pixmap * fz_new_pixmap_with_bbox(fz_context * ctx, fz_colorspace * colorspace, const fz_irect * bbox, fz_separations * seps, int alpha);
fz_pixmap * fz_new_pixmap_with_bbox_and_data(fz_context * ctx, fz_colorspace * colorspace, const fz_irect * rect, fz_separations * seps, int alpha, unsigned char * samples);
int fz_pixmap_height(fz_context * ctx, fz_pixmap * pix);
unsigned char * fz_pixmap_samples(fz_context * ctx, fz_pixmap * pix);
int fz_pixmap_stride(fz_context * ctx, fz_pixmap * pix);
int fz_pixmap_width(fz_context * ctx, fz_pixmap * pix);
void fz_set_pixmap_resolution(fz_context * ctx, fz_pixmap * pix, int xres, int yres);

// structured-text.h
void fz_drop_stext_page(fz_context * ctx, fz_stext_page * page);
fz_stext_page * fz_new_stext_page(fz_context * ctx, const fz_rect * mediabox);
fz_device * fz_new_stext_device(fz_context * ctx, fz_stext_page * page, const fz_stext_options * options);
const fz_stext_char * fz_stext_char_at(fz_context * ctx, fz_stext_page  *page, int idx);
int fz_stext_char_count(fz_context * ctx, fz_stext_page * page);

// util
fz_pixmap * fz_new_pixmap_from_page(fz_context * ctx, fz_page * page, const fz_matrix * ctm, fz_colorspace * cs, int alpha);
fz_pixmap * fz_new_pixmap_from_page_number(fz_context * ctx, fz_document * doc, int number, const fz_matrix * ctm, fz_colorspace * cs, int alpha);
fz_pixmap *  fz_new_pixmap_from_page_contents(fz_context *  ctx, fz_page *  page, const fz_matrix *  ctm, fz_colorspace *  cs, int alpha);
fz_stext_page * fz_new_stext_page_from_page(fz_context * ctx, fz_page * page, const fz_stext_options * options);
fz_stext_page * fz_new_stext_page_from_page_number(fz_context * ctx, fz_document * doc, int number, const fz_stext_options * options);
fz_buffer * fz_new_buffer_from_stext_page(fz_context * ctx, fz_stext_page * text);
fz_buffer * fz_new_buffer_from_page(fz_context * ctx, fz_page * page, const fz_stext_options * options);
fz_buffer * fz_new_buffer_from_page_number(fz_context * ctx, fz_document * doc, int number, const fz_stext_options * options);

// from pdf.h
fz_page * fz_load_page (fz_context * ctx, fz_document * doc, int number);
